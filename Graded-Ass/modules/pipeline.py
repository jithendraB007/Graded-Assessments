"""pipeline.py — Watch-folder pipeline for automated question paper generation.

Architecture
────────────
One folder per course lives under the watch root (default: ./watch/):

    watch/
        ENG101/
            config.json     ← saved by the Streamlit Course Setup tab
            template.docx   ← uploaded once by the teacher
            *.csv           ← teacher drops a new question bank here
            output/
                *.docx      ← generated papers land here (status: pending)

When the PipelineHandler detects a new *.csv in a course folder it:
    1. Loads config.json + template.docx
    2. Loads the CSV via load_dataset()
    3. Selects questions (judge-aware if API key available, else plain)
    4. Generates the paper via generate_paper() with the CourseConfig
    5. Saves the .docx to output/
    6. Appends a PendingPaper record to PendingQueue (persisted as JSON)

Thread-safety
─────────────
watchdog runs its handler in a background thread.  PendingQueue uses a
threading.Lock around every read/write to the backing JSON file so Streamlit
(main thread) and the watcher (background thread) can both access the queue
safely.
"""
from __future__ import annotations

import io
import json
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# PendingPaper + PendingQueue
# ---------------------------------------------------------------------------

_STATUS_PENDING    = "pending"
_STATUS_DOWNLOADED = "downloaded"
_STATUS_ERROR      = "error"


@dataclass
class PendingPaper:
    """Represents one generated paper waiting for the teacher to review/download."""
    id: str
    course_code: str
    csv_filename: str
    output_path: str           # absolute path to the generated .docx
    status: str                # "pending" | "downloaded" | "error"
    created_at: str            # ISO-8601 timestamp
    pass_count: int = 0
    revise_count: int = 0
    fail_count: int = 0
    rebalance_log: list[str] = field(default_factory=list)
    error_message: str = ""


class PendingQueue:
    """Thread-safe queue of PendingPaper objects, backed by a JSON file."""

    def __init__(self, queue_file: Path) -> None:
        self._file  = queue_file
        self._lock  = threading.Lock()
        self._papers: list[PendingPaper] = []
        self.load()

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def load(self) -> None:
        with self._lock:
            if self._file.exists():
                try:
                    with open(self._file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._papers = [PendingPaper(**p) for p in data]
                except Exception:
                    self._papers = []
            else:
                self._papers = []

    def _save(self) -> None:
        """Internal save (must be called while holding _lock)."""
        self._file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump([asdict(p) for p in self._papers], f, indent=2)

    # ------------------------------------------------------------------ #
    # Mutations                                                            #
    # ------------------------------------------------------------------ #

    def add(self, paper: PendingPaper) -> None:
        with self._lock:
            self._papers.append(paper)
            self._save()

    def mark_downloaded(self, paper_id: str) -> None:
        with self._lock:
            for p in self._papers:
                if p.id == paper_id:
                    p.status = _STATUS_DOWNLOADED
                    break
            self._save()

    # ------------------------------------------------------------------ #
    # Queries                                                              #
    # ------------------------------------------------------------------ #

    def get_all(self) -> list[PendingPaper]:
        with self._lock:
            return list(self._papers)

    def get_pending(self) -> list[PendingPaper]:
        with self._lock:
            return [p for p in self._papers if p.status == _STATUS_PENDING]

    def pending_count(self) -> int:
        with self._lock:
            return sum(1 for p in self._papers if p.status == _STATUS_PENDING)


# ---------------------------------------------------------------------------
# Pipeline run — called from the watchdog handler
# ---------------------------------------------------------------------------

def run_pipeline(
    course_dir: Path,
    csv_path: Path,
    queue: PendingQueue,
    mistral_api_key: str = "",
    mistral_model: str = "mistral-small-latest",
) -> None:
    """Full pipeline: CSV → question paper → PendingPaper in queue.

    Designed to run in the watchdog background thread.  All imports are local
    so this module can be imported without triggering heavy dependencies at
    startup.
    """
    from modules.course_config import CourseConfig
    from modules.dataset_loader import load_dataset
    from modules.template_parser import parse_template
    from modules.question_selector import select_questions, select_questions_judge_aware
    from modules.paper_generator import generate_paper

    paper_id   = str(uuid.uuid4())[:8]
    created_at = datetime.now().isoformat(timespec="seconds")
    course_code = course_dir.name
    rebalance_log: list[str] = []
    pass_count = revise_count = fail_count = 0

    try:
        # 1. Load course config
        config_path = course_dir / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"config.json not found in {course_dir}")
        config = CourseConfig.load(config_path)

        # 2. Load template
        template_path = course_dir / "template.docx"
        if not template_path.exists():
            raise FileNotFoundError(f"template.docx not found in {course_dir}")
        with open(template_path, "rb") as f:
            tmpl_buf = io.BytesIO(f.read())

        # 3. Load CSV
        with open(csv_path, "rb") as f:
            csv_buf = io.BytesIO(f.read())
        ds = load_dataset(csv_buf, csv_path.name)

        # 4. Parse template
        template_result = parse_template(tmpl_buf)

        # 5. Select questions (judge-aware if API key is available)
        if mistral_api_key:
            from modules.judge import load_judge
            judge = load_judge()
            # Build PlaceholderRecord list from config sections instead of template
            # (pipeline uses config-driven counts, not placeholder count hints)
            placeholders = template_result.placeholders
            # Override counts from config sections
            easy_count   = sum(
                s.difficulty_counts.get("easy", 0) for s in config.sections
            )
            medium_count = sum(
                s.difficulty_counts.get("medium", 0) for s in config.sections
            )
            hard_count   = sum(
                s.difficulty_counts.get("hard", 0) for s in config.sections
            )
            selection_result, rebalance_log = select_questions_judge_aware(
                placeholders=placeholders,
                df=ds.df,
                topic=config.topic,
                subtopic=config.subtopic,
                easy_count=easy_count,
                medium_count=medium_count,
                hard_count=hard_count,
                judge=judge,
                api_key=mistral_api_key,
                model=mistral_model,
            )
            # Tally judge stats from assignments
            from modules.judge import judge_single_question, _make_lm
            import dspy
            lm = _make_lm(mistral_api_key, mistral_model)
            with dspy.context(lm=lm):
                for _, assigned_df in selection_result.assignments.items():
                    for _, row in assigned_df.iterrows():
                        try:
                            jr = judge_single_question(judge, row)
                            if jr.overall_decision == "Pass":
                                pass_count += 1
                            elif jr.overall_decision == "Revise":
                                revise_count += 1
                            else:
                                fail_count += 1
                        except Exception:
                            pass
        else:
            # No API key — use plain selection with config-driven counts
            easy_count   = sum(s.difficulty_counts.get("easy", 0) for s in config.sections)
            medium_count = sum(s.difficulty_counts.get("medium", 0) for s in config.sections)
            hard_count   = sum(s.difficulty_counts.get("hard", 0) for s in config.sections)
            selection_result = select_questions(
                placeholders=template_result.placeholders,
                df=ds.df,
                topic=config.topic,
                subtopic=config.subtopic,
                easy_count=easy_count,
                medium_count=medium_count,
                hard_count=hard_count,
            )

        # 6. Generate paper
        buf = generate_paper(template_result, selection_result, course_config=config)

        # 7. Write .docx to output folder
        output_dir = Path(config.output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_filename = f"{course_code}_{csv_path.stem}_{ts}.docx"
        out_path = output_dir / out_filename
        with open(out_path, "wb") as f:
            f.write(buf.getvalue())

        # 8. Queue the pending paper
        queue.add(PendingPaper(
            id=paper_id,
            course_code=course_code,
            csv_filename=csv_path.name,
            output_path=str(out_path),
            status=_STATUS_PENDING,
            created_at=created_at,
            pass_count=pass_count,
            revise_count=revise_count,
            fail_count=fail_count,
            rebalance_log=rebalance_log,
        ))

    except Exception as exc:
        queue.add(PendingPaper(
            id=paper_id,
            course_code=course_code,
            csv_filename=csv_path.name,
            output_path="",
            status=_STATUS_ERROR,
            created_at=created_at,
            error_message=str(exc),
        ))


# ---------------------------------------------------------------------------
# Watchdog file-system handler
# ---------------------------------------------------------------------------

def _watchdog_available() -> bool:
    try:
        import watchdog  # noqa: F401
        return True
    except ImportError:
        return False


def start_watcher(
    watch_root: Path,
    queue: PendingQueue,
    mistral_api_key: str = "",
    mistral_model: str = "mistral-small-latest",
):
    """Start a watchdog Observer that monitors all course sub-folders.

    Returns the Observer object (call .stop() to halt it) or None if
    watchdog is not installed.
    """
    if not _watchdog_available():
        return None

    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent

    class _Handler(FileSystemEventHandler):
        def on_created(self, event: FileCreatedEvent) -> None:
            if event.is_directory:
                return
            p = Path(event.src_path)
            if p.suffix.lower() != ".csv":
                return
            # The CSV must be directly inside a course folder
            # (not inside the output/ sub-folder)
            course_dir = p.parent
            if course_dir.name == "output":
                return
            # Ensure the course folder has a config.json
            if not (course_dir / "config.json").exists():
                return
            # Run pipeline in a fresh thread so the handler returns quickly
            t = threading.Thread(
                target=run_pipeline,
                args=(course_dir, p, queue, mistral_api_key, mistral_model),
                daemon=True,
            )
            t.start()

    watch_root.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(_Handler(), str(watch_root), recursive=True)
    observer.daemon = True
    observer.start()
    return observer

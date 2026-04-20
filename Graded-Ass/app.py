"""app.py — Question Paper Generator  (3-tab redesign)

Tabs:
  1. Generate     — manual upload → configure → generate → judge (existing flow)
  2. Course Setup — configure branding + section schema per course; save to watch folder
  3. Pending Papers — pipeline queue: watch-folder toggle + pending paper downloads
"""
from __future__ import annotations

import io
import json
import os
import shutil
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from modules.dataset_loader import load_dataset
from modules.template_parser import parse_template
from modules.question_selector import select_questions
from modules.paper_generator import generate_paper
from modules.course_config import (
    CourseConfig, BrandingConfig, SectionConfig, default_english_config
)
from modules.pipeline import PendingQueue, start_watcher, _watchdog_available

try:
    from modules.judge import run_judge_on_assignments, JudgeResult
    JUDGE_AVAILABLE = True
except ImportError:
    JUDGE_AVAILABLE = False

TRAINING_DATA_PATH = Path("data/judge_training.jsonl")
ARTIFACT_PATH      = Path("artifacts/english_judge_optimized.json")
WATCH_ROOT         = Path("watch")
QUEUE_FILE         = Path("data/pending_queue.json")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Question Paper Generator",
    page_icon="📄",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------

if "pending_queue" not in st.session_state:
    st.session_state["pending_queue"] = PendingQueue(QUEUE_FILE)
if "watcher_observer" not in st.session_state:
    st.session_state["watcher_observer"] = None
if "watcher_active" not in st.session_state:
    st.session_state["watcher_active"] = False

queue: PendingQueue = st.session_state["pending_queue"]
pending_count = queue.pending_count()

# ---------------------------------------------------------------------------
# Sidebar — settings shared across tabs
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Judge Settings")

    api_key_from_env = os.environ.get("MISTRAL_API_KEY", "")
    if api_key_from_env:
        st.success("API key loaded from .env")
        mistral_api_key = api_key_from_env
    else:
        mistral_api_key = st.text_input(
            "Mistral API Key",
            type="password",
            placeholder="sk-...",
            help="Get your key at console.mistral.ai — or add MISTRAL_API_KEY to a .env file.",
        )

    model_from_env = os.environ.get("MISTRAL_MODEL", "")
    _models = ["mistral-small-latest", "open-mistral-nemo", "mistral-medium-latest"]
    mistral_model = st.selectbox(
        "Judge Model",
        _models,
        index=_models.index(model_from_env) if model_from_env in _models else 0,
    )

    enable_judge = st.toggle(
        "Enable Quality Judge",
        value=bool(mistral_api_key) and JUDGE_AVAILABLE,
        disabled=not (bool(mistral_api_key) and JUDGE_AVAILABLE),
    )

    st.markdown("---")
    st.header("🔬 Judge Optimization")
    n_examples = (
        sum(1 for line in TRAINING_DATA_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip())
        if TRAINING_DATA_PATH.exists() else 0
    )
    st.caption(f"Labelled examples: **{n_examples}**")
    if ARTIFACT_PATH.exists():
        st.success("Optimized judge loaded")
    else:
        st.info("Running zero-shot (no artifact yet)")

    opt_disabled = n_examples < 5 or not bool(mistral_api_key)
    if st.button("Optimize Judge Prompt", disabled=opt_disabled):
        with st.spinner("Optimizing…"):
            from optimize.judge_optimizer import optimize
            msg = optimize()
        st.success(msg)
        st.rerun()

    st.markdown("---")
    st.header("📋 Placeholder Guide")
    st.markdown("""
**Format:** `{{DIFFICULTY_TYPE}}`

| Placeholder | Inserts |
|---|---|
| `{{EASY_MCQ}}` | Easy MCQ |
| `{{MEDIUM_MCQ}}` | Medium MCQ |
| `{{HARD_MCQ}}` | Hard MCQ |
| `{{EASY_LONG_ANSWER}}` | Easy long answer |
| `{{MEDIUM_LONG_ANSWER}}` | Medium long answer |
| `{{HARD_LONG_ANSWER}}` | Hard long answer |

Aliases: `SA`=Short Answer · `LA`=Long Answer
""")

# ---------------------------------------------------------------------------
# Helpers (shared across tabs)
# ---------------------------------------------------------------------------

DECISION_COLOR = {"Pass": "green", "Revise": "orange", "Fail": "red"}
DECISION_ICON  = {"Pass": "✅", "Revise": "⚠️", "Fail": "❌"}

def _badge(decision: str) -> str:
    color = DECISION_COLOR.get(decision, "grey")
    icon  = DECISION_ICON.get(decision, "•")
    return f'<span style="color:{color};font-weight:600">{icon} {decision}</span>'

def _criteria_row(label: str, value: str) -> str:
    bad_kw = {"major issue", "weak", "unclear", "fail", "too easy",
              "too hard", "too simple", "too complex"}
    color = "red" if any(b in value.lower() for b in bad_kw) else "inherit"
    return f"**{label}:** <span style='color:{color}'>{value}</span>"

def _count_decisions(results) -> dict:
    counts = {"Pass": 0, "Revise": 0, "Fail": 0}
    for r in results:
        counts[r.overall_decision] = counts.get(r.overall_decision, 0) + 1
    return counts

def _save_feedback(row_dict: dict, confirmed_decision: str) -> None:
    TRAINING_DATA_PATH.parent.mkdir(exist_ok=True)
    entry = {k: v for k, v in row_dict.items()}
    entry["expected_overall_decision"] = confirmed_decision
    with open(TRAINING_DATA_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# ---------------------------------------------------------------------------
# Tab labels (inject pending badge into tab 3)
# ---------------------------------------------------------------------------

tab_label_generate = "📄 Generate"
tab_label_setup    = "⚙️ Course Setup"
tab_label_pending  = (
    f"🗂️ Pending Papers  🔴 {pending_count}"
    if pending_count > 0 else "🗂️ Pending Papers"
)

tab_gen, tab_setup, tab_pipeline = st.tabs(
    [tab_label_generate, tab_label_setup, tab_label_pending]
)

# ============================================================================
# TAB 1 — Generate (existing interactive flow)
# ============================================================================

with tab_gen:
    st.subheader("Generate a Question Paper")
    st.caption(
        "Upload your Word template (.docx) and question dataset (.csv/.xlsx).  "
        "The app fills every `{{PLACEHOLDER}}` with formatted questions."
    )

    # Pre-fill from loaded course config if available
    saved_cc: CourseConfig | None = st.session_state.get("course_config")

    # ── Step 1: Upload ────────────────────────────────────────────────────────
    st.markdown("#### Step 1 — Upload Files")
    c1, c2 = st.columns(2)
    with c1:
        template_file = st.file_uploader(
            "Word Template (.docx)",
            type=["docx"],
            key="gen_template",
        )
    with c2:
        dataset_file = st.file_uploader(
            "Question Dataset (.csv or .xlsx)",
            type=["csv", "xlsx", "xls"],
            key="gen_dataset",
        )

    if dataset_file is not None:
        try:
            import pandas as pd
            ext = dataset_file.name.rsplit(".", 1)[-1].lower()
            buf = io.BytesIO(dataset_file.read())
            preview_df = (
                pd.read_csv(buf) if ext == "csv"
                else pd.read_excel(buf, engine="openpyxl")
            )
            dataset_file.seek(0)
            with st.expander(f"Preview ({len(preview_df)} rows)", expanded=False):
                st.dataframe(preview_df.head(10), use_container_width=True)
        except Exception:
            pass

    st.markdown("---")

    # ── Step 2: Configure ────────────────────────────────────────────────────
    st.markdown("#### Step 2 — Configure Paper")

    cc_topic    = saved_cc.topic    if saved_cc else ""
    cc_subtopic = saved_cc.subtopic if saved_cc else ""
    cc_easy   = sum(s.difficulty_counts.get("easy",   0) for s in saved_cc.sections) if saved_cc else 5
    cc_medium = sum(s.difficulty_counts.get("medium", 0) for s in saved_cc.sections) if saved_cc else 3
    cc_hard   = sum(s.difficulty_counts.get("hard",   0) for s in saved_cc.sections) if saved_cc else 2

    gc1, gc2 = st.columns(2)
    with gc1:
        topic    = st.text_input("Topic",    value=cc_topic,    placeholder="e.g. English Grammar")
    with gc2:
        subtopic = st.text_input("Subtopic", value=cc_subtopic, placeholder="e.g. Tenses")

    gc3, gc4, gc5 = st.columns(3)
    with gc3:
        easy_count   = st.number_input("Easy Questions",   min_value=0, value=cc_easy,   step=1)
    with gc4:
        medium_count = st.number_input("Medium Questions", min_value=0, value=cc_medium, step=1)
    with gc5:
        hard_count   = st.number_input("Hard Questions",   min_value=0, value=cc_hard,   step=1)

    st.caption(f"Total: **{int(easy_count) + int(medium_count) + int(hard_count)}** questions")

    # Optional: use loaded course config for branding/section headers
    use_cc_branding = False
    if saved_cc:
        use_cc_branding = st.checkbox(
            f"Apply branding & section headers from course config ({saved_cc.course_code})",
            value=True,
        )

    st.markdown("---")

    # ── Step 3: Generate ─────────────────────────────────────────────────────
    st.markdown("#### Step 3 — Generate")
    files_ready = template_file is not None and dataset_file is not None
    if not files_ready:
        st.info("Upload both files above to enable generation.")

    generate_clicked = st.button(
        "Generate Question Paper",
        disabled=not files_ready,
        type="primary",
        key="gen_button",
    )

    if generate_clicked and files_ready:
        if not topic.strip():
            st.error("Please enter a Topic.")
            st.stop()
        if not subtopic.strip():
            st.error("Please enter a Subtopic.")
            st.stop()

        all_warnings: list[str] = []
        with st.spinner("Processing…"):
            try:
                dataset_result  = load_dataset(io.BytesIO(dataset_file.read()), dataset_file.name)
                all_warnings.extend(dataset_result.warnings)

                template_result = parse_template(io.BytesIO(template_file.read()))
                all_warnings.extend(template_result.warnings)

                if not template_result.placeholders:
                    st.warning("No `{{PLACEHOLDER}}` markers found in the template.")
                    st.session_state.update({
                        "output_bytes": template_file.getvalue(),
                        "generation_done": True,
                        "judge_results": [],
                        "selection_result": None,
                        "dataset_df": dataset_result.df,
                    })
                else:
                    selection_result = select_questions(
                        placeholders=template_result.placeholders,
                        df=dataset_result.df,
                        topic=topic, subtopic=subtopic,
                        easy_count=int(easy_count),
                        medium_count=int(medium_count),
                        hard_count=int(hard_count),
                    )
                    for err in selection_result.errors:
                        all_warnings.append(
                            f"Shortfall for `{err.placeholder_raw}`: "
                            f"requested {err.requested}, only {err.available} available."
                        )

                    cc_arg = saved_cc if use_cc_branding else None
                    output_buffer = generate_paper(template_result, selection_result, cc_arg)
                    total_placed  = sum(len(df) for df in selection_result.assignments.values())

                    st.success(
                        f"Paper generated: **{total_placed} question(s)** placed across "
                        f"**{len(template_result.placeholders)} section(s)**."
                    )
                    st.session_state.update({
                        "output_bytes":     output_buffer.getvalue(),
                        "generation_done":  True,
                        "judge_results":    [],
                        "selection_result": selection_result,
                        "dataset_df":       dataset_result.df,
                    })

            except ValueError as exc:
                st.error(f"Configuration error: {exc}")
                st.stop()
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
                st.exception(exc)
                st.stop()

        if all_warnings:
            with st.expander("Warnings", expanded=True):
                for w in all_warnings:
                    st.warning(w)

    # Download button
    if st.session_state.get("generation_done") and "output_bytes" in st.session_state:
        st.download_button(
            label="⬇️ Download question_paper.docx",
            data=st.session_state["output_bytes"],
            file_name="question_paper.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    st.markdown("---")

    # ── Step 4: Quality Judge ─────────────────────────────────────────────────
    st.markdown("#### Step 4 — Quality Judge")

    sel_result    = st.session_state.get("selection_result")
    already_judged = bool(st.session_state.get("judge_results"))

    if not st.session_state.get("generation_done"):
        st.info("Generate a paper first (Step 3).")
    elif not JUDGE_AVAILABLE:
        st.warning("Install `dspy-ai` to enable the judge.")
    elif not enable_judge or not mistral_api_key:
        st.info("Add your Mistral API key in the sidebar and enable the judge toggle.")
    elif sel_result is None:
        st.info("No questions were inserted.")
    else:
        judge_btn = st.button(
            "Run Quality Judge" if not already_judged else "Re-run Quality Judge",
            type="secondary",
        )
        if judge_btn:
            assignments = sel_result.assignments
            total_qs = sum(len(df) for df in assignments.values() if not df.empty)
            with st.spinner(f"Judging {total_qs} question(s) with {mistral_model}…"):
                try:
                    results = run_judge_on_assignments(
                        assignments=assignments,
                        api_key=mistral_api_key,
                        model=mistral_model,
                    )
                    st.session_state["judge_results"] = results
                except Exception as exc:
                    st.error(f"Judge error: {exc}")
                    st.stop()

    judge_results = st.session_state.get("judge_results", [])
    if judge_results:
        counts = _count_decisions(judge_results)
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("✅ Pass",   counts.get("Pass",   0))
        mc2.metric("⚠️ Revise", counts.get("Revise", 0))
        mc3.metric("❌ Fail",   counts.get("Fail",   0))

        filter_choice = st.radio("Show", ["All", "Pass", "Revise", "Fail"], horizontal=True)
        filtered = (
            judge_results if filter_choice == "All"
            else [r for r in judge_results if r.overall_decision == filter_choice]
        )
        st.caption(f"Showing {len(filtered)} of {len(judge_results)} questions")

        for i, result in enumerate(filtered):
            header = (
                f"Q{i+1} [{result.difficulty.title()} {result.question_type.upper()}]"
                f" — {result.question_text[:80]}{'…' if len(result.question_text) > 80 else ''}"
            )
            with st.expander(header, expanded=(result.overall_decision != "Pass")):
                st.markdown(_badge(result.overall_decision) + f"  `{result.question_id}`",
                            unsafe_allow_html=True)
                clines = [
                    _criteria_row("Grammatical accuracy",     result.grammatical_accuracy),
                    _criteria_row("Clarity",                  result.clarity),
                    _criteria_row("Difficulty alignment",     result.difficulty_alignment),
                    _criteria_row("Language level",           result.language_level_appropriateness),
                    _criteria_row("Instruction clarity",      result.instruction_clarity),
                ]
                if result.question_type == "mcq":
                    clines.append(_criteria_row("Distractor quality", result.distractor_quality))
                clines.append(_criteria_row("Format compliance", result.format_compliance))
                for line in clines:
                    st.markdown(line, unsafe_allow_html=True)
                if result.priority_reason:
                    st.markdown(f"**Reason:** {result.priority_reason}")
                if result.revision_feedback:
                    st.info(f"💡 {result.revision_feedback}")

                st.markdown("**Confirm verdict:**")
                fb1, fb2, fb3 = st.columns(3)
                kp = f"fb_{result.question_id}_{i}"
                ds_df = st.session_state.get("dataset_df")
                row_dict: dict = {}
                if ds_df is not None and not ds_df.empty:
                    m = ds_df[ds_df["question_id"].astype(str) == result.question_id]
                    if not m.empty:
                        row_dict = m.iloc[0].to_dict()
                base = row_dict | {
                    "question_id": result.question_id,
                    "question_text": result.question_text,
                    "question_type": result.question_type,
                    "difficulty": result.difficulty,
                }
                if fb1.button("✅ Confirm Pass",  key=f"{kp}_pass"):
                    _save_feedback(base, "Pass");   st.toast(f"Saved Pass for {result.question_id}")
                if fb2.button("⚠️ Mark Revise",   key=f"{kp}_revise"):
                    _save_feedback(base, "Revise"); st.toast(f"Saved Revise for {result.question_id}")
                if fb3.button("❌ Mark Fail",      key=f"{kp}_fail"):
                    _save_feedback(base, "Fail");   st.toast(f"Saved Fail for {result.question_id}")

        n_col = sum(
            1 for line in TRAINING_DATA_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ) if TRAINING_DATA_PATH.exists() else 0
        if n_col > 0:
            needed = max(0, 5 - n_col)
            if needed:
                st.caption(f"📊 {n_col} label(s) saved — {needed} more to unlock optimization.")
            else:
                st.caption(f"📊 {n_col} label(s) saved — click **Optimize Judge Prompt** in sidebar.")


# ============================================================================
# TAB 2 — Course Setup
# ============================================================================

with tab_setup:
    st.subheader("Course Configuration")
    st.caption(
        "Define branding and section schema for a course.  "
        "The pipeline will reuse this config every time a CSV is dropped into the course folder."
    )

    # List existing courses
    existing_courses = [d.name for d in WATCH_ROOT.iterdir() if d.is_dir()] if WATCH_ROOT.exists() else []
    if existing_courses:
        with st.expander("Existing course configs", expanded=False):
            for code in existing_courses:
                cfg_path = WATCH_ROOT / code / "config.json"
                if cfg_path.exists():
                    col_a, col_b = st.columns([4, 1])
                    col_a.write(f"**{code}** — {cfg_path}")
                    if col_b.button("Load", key=f"load_{code}"):
                        st.session_state["course_config"] = CourseConfig.load(cfg_path)
                        st.success(f"Loaded config for {code}")
                        st.rerun()

    st.markdown("---")
    st.markdown("#### Course Identity")
    sc1, sc2 = st.columns(2)
    with sc1:
        cc_code = st.text_input("Course Code", placeholder="ENG101")
    with sc2:
        cc_name = st.text_input("Course Name", placeholder="English Grammar")

    sc3, sc4 = st.columns(2)
    with sc3:
        cc_topic    = st.text_input("Topic",    placeholder="English Grammar",
                                     help="Must match the `topic` column in your CSV exactly.")
    with sc4:
        cc_subtopic = st.text_input("Subtopic", placeholder="Tenses",
                                     help="Must match the `subtopic` column in your CSV exactly.")

    st.markdown("---")
    st.markdown("#### Exam Settings")
    es1, es2 = st.columns(2)
    with es1:
        cc_exam_title  = st.text_input("Exam Title",    value="ANNUAL EXAMINATION")
    with es2:
        cc_time        = st.text_input("Time Allowed",  value="3 Hours")

    st.markdown("---")
    st.markdown("#### Branding")
    br1, br2 = st.columns(2)
    with br1:
        cc_inst   = st.text_input("Institution Name", placeholder="XYZ Engineering College")
        cc_dept   = st.text_input("Department",       placeholder="Department of English")
    with br2:
        cc_reg    = st.text_input("Regulation",       placeholder="2021 Regulation")
        logo_file = st.file_uploader("Institution Logo (.png / .jpg)", type=["png", "jpg", "jpeg"],
                                      key="logo_upload")

    st.markdown("---")
    st.markdown("#### Section Schema")
    st.caption("Define up to 3 exam sections (PART A, B, C).  Adjust types, counts, and marks.")

    _Q_TYPES = ["mcq", "short_answer", "long_answer", "case_study"]
    sections_data = []

    for part_letter, part_defaults in [
        ("A", {"title": "Multiple Choice Questions",    "qt": "mcq",         "either_or": False, "mpq": 1,  "e": 5, "m": 5, "h": 5}),
        ("B", {"title": "Detailed Answer Questions",    "qt": "long_answer",  "either_or": True,  "mpq": 14, "e": 2, "m": 4, "h": 4}),
        ("C", {"title": "Case Study / Application",     "qt": "long_answer",  "either_or": False, "mpq": 10, "e": 0, "m": 0, "h": 1}),
    ]:
        with st.expander(f"PART {part_letter}", expanded=(part_letter == "A")):
            p1, p2, p3, p4 = st.columns([2, 1, 1, 1])
            sec_title   = p1.text_input("Section Title", value=part_defaults["title"], key=f"title_{part_letter}")
            sec_type    = p2.selectbox("Question Type", _Q_TYPES,
                                        index=_Q_TYPES.index(part_defaults["qt"]),
                                        key=f"qtype_{part_letter}")
            sec_either  = p3.checkbox("Either-Or", value=part_defaults["either_or"],
                                       help="Pair questions as N(a)/(OR)/N(b)",
                                       key=f"eo_{part_letter}")
            sec_mpq     = p4.number_input("Marks/Q", min_value=0.5, value=float(part_defaults["mpq"]),
                                           step=0.5, key=f"mpq_{part_letter}")

            sec_inst = st.text_input("Instruction", value="Answer all the Questions",
                                      key=f"inst_{part_letter}")

            dc1, dc2, dc3 = st.columns(3)
            sec_easy   = dc1.number_input("Easy",   min_value=0, value=part_defaults["e"], step=1, key=f"easy_{part_letter}")
            sec_medium = dc2.number_input("Medium", min_value=0, value=part_defaults["m"], step=1, key=f"med_{part_letter}")
            sec_hard   = dc3.number_input("Hard",   min_value=0, value=part_defaults["h"], step=1, key=f"hard_{part_letter}")

            n_q = int(sec_easy) + int(sec_medium) + int(sec_hard)
            if sec_either:
                pairs = n_q // 2
                total_m = pairs * sec_mpq
                st.caption(f"{n_q} questions → {pairs} either-or pairs × {sec_mpq} marks = **{int(total_m)} marks**")
            else:
                total_m = n_q * sec_mpq
                st.caption(f"{n_q} questions × {sec_mpq} marks = **{int(total_m)} marks**")

            sections_data.append(SectionConfig(
                part=part_letter,
                label=f"PART {part_letter}",
                title=sec_title,
                instruction=sec_inst,
                question_type=sec_type,
                either_or=sec_either,
                marks_per_q=float(sec_mpq),
                difficulty_counts={
                    "easy":   int(sec_easy),
                    "medium": int(sec_medium),
                    "hard":   int(sec_hard),
                },
            ))

    grand_total = sum(
        (sum(s.difficulty_counts.values()) // 2 if s.either_or else sum(s.difficulty_counts.values()))
        * s.marks_per_q
        for s in sections_data
    )
    st.markdown(f"**Grand Total Marks: {int(grand_total)}**")

    st.markdown("---")
    st.markdown("#### Template for This Course")
    tmpl_upload = st.file_uploader(
        "Upload .docx template (saved to watch/{course_code}/template.docx)",
        type=["docx"],
        key="cc_template",
    )

    st.markdown("---")
    save_col, _ = st.columns([1, 3])
    save_clicked = save_col.button("💾 Save Course Config", type="primary",
                                    disabled=not cc_code.strip())

    if save_clicked:
        if not cc_code.strip():
            st.error("Course Code is required.")
        else:
            course_dir = WATCH_ROOT / cc_code.strip()
            course_dir.mkdir(parents=True, exist_ok=True)
            (course_dir / "output").mkdir(exist_ok=True)

            # Handle logo
            logo_path_str = ""
            if logo_file is not None:
                logo_dest = course_dir / logo_file.name
                with open(logo_dest, "wb") as f:
                    f.write(logo_file.read())
                logo_path_str = str(logo_dest)

            # Handle template
            if tmpl_upload is not None:
                tmpl_dest = course_dir / "template.docx"
                with open(tmpl_dest, "wb") as f:
                    f.write(tmpl_upload.read())

            config = CourseConfig(
                course_code=cc_code.strip(),
                course_name=cc_name.strip(),
                topic=cc_topic.strip(),
                subtopic=cc_subtopic.strip(),
                branding=BrandingConfig(
                    institution_name=cc_inst.strip(),
                    department=cc_dept.strip(),
                    regulation=cc_reg.strip(),
                    logo_path=logo_path_str or None,
                ),
                sections=sections_data,
                exam_title=cc_exam_title.strip(),
                time_allowed=cc_time.strip(),
                watch_folder=str(course_dir),
                output_folder=str(course_dir / "output"),
            )
            config.save(course_dir / "config.json")
            st.session_state["course_config"] = config
            st.success(
                f"Config saved to `{course_dir / 'config.json'}`  |  "
                f"Drop CSVs into `{course_dir}` to trigger the pipeline."
            )


# ============================================================================
# TAB 3 — Pending Papers + Watch Folder
# ============================================================================

with tab_pipeline:
    st.subheader("Pipeline — Pending Papers")

    # ── Watch folder toggle ───────────────────────────────────────────────────
    watcher_col, status_col = st.columns([2, 3])

    with watcher_col:
        if not _watchdog_available():
            st.warning("`watchdog` not installed — run `pip install watchdog` to enable.")
            watcher_on = False
        else:
            watcher_on = st.toggle(
                "Watch Folder (auto-generate on CSV drop)",
                value=st.session_state["watcher_active"],
                key="watch_toggle",
            )

    if watcher_on and not st.session_state["watcher_active"]:
        observer = start_watcher(
            WATCH_ROOT, queue,
            mistral_api_key=mistral_api_key,
            mistral_model=mistral_model,
        )
        st.session_state["watcher_observer"] = observer
        st.session_state["watcher_active"]   = True
        status_col.success(f"Watching `{WATCH_ROOT.resolve()}` — drop a CSV into any course subfolder.")

    elif not watcher_on and st.session_state["watcher_active"]:
        obs = st.session_state.get("watcher_observer")
        if obs is not None:
            try:
                obs.stop()
                obs.join(timeout=2)
            except Exception:
                pass
        st.session_state["watcher_observer"] = None
        st.session_state["watcher_active"]   = False
        status_col.info("Watcher stopped.")

    elif st.session_state["watcher_active"]:
        status_col.success(f"Watching `{WATCH_ROOT.resolve()}`")

    st.markdown("---")

    # ── Refresh button ────────────────────────────────────────────────────────
    if st.button("🔄 Refresh Queue"):
        queue.load()
        st.rerun()

    # ── Pending papers table ──────────────────────────────────────────────────
    all_papers = queue.get_all()

    if not all_papers:
        st.info(
            "No papers in queue yet.  "
            "Enable the Watch Folder toggle and drop a CSV into a course folder to start."
        )
    else:
        for paper in reversed(all_papers):   # newest first
            status_emoji = {"pending": "🟡", "downloaded": "✅", "error": "🔴"}.get(paper.status, "•")
            header = (
                f"{status_emoji} **{paper.course_code}** — `{paper.csv_filename}` "
                f"— {paper.created_at[:16]}"
            )
            with st.expander(header, expanded=(paper.status == "pending")):
                if paper.status == "error":
                    st.error(f"Pipeline error: {paper.error_message}")
                else:
                    qc1, qc2, qc3 = st.columns(3)
                    qc1.metric("✅ Pass",   paper.pass_count)
                    qc2.metric("⚠️ Revise", paper.revise_count)
                    qc3.metric("❌ Fail",   paper.fail_count)

                    if paper.rebalance_log:
                        with st.expander("Quality & Rebalance Log", expanded=False):
                            for entry in paper.rebalance_log:
                                st.warning(entry)

                    if paper.status == "pending" and paper.output_path:
                        out_p = Path(paper.output_path)
                        if out_p.exists():
                            with open(out_p, "rb") as f:
                                docx_bytes = f.read()
                            if st.download_button(
                                label=f"⬇️ Download {out_p.name}",
                                data=docx_bytes,
                                file_name=out_p.name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_{paper.id}",
                            ):
                                queue.mark_downloaded(paper.id)
                                st.rerun()
                        else:
                            st.warning(f"Output file not found: {paper.output_path}")

                    elif paper.status == "downloaded":
                        st.success("Downloaded ✓")

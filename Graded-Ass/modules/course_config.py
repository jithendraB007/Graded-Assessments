"""course_config.py — Course configuration dataclasses for the pipeline.

A CourseConfig is created once per course via the Streamlit Course Setup tab
and saved as config.json inside the course's watch folder:

    watch/ENG101/config.json

The pipeline loads this config automatically whenever a CSV is dropped into
the same folder.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Sub-configs
# ---------------------------------------------------------------------------

@dataclass
class BrandingConfig:
    """Institution identity that appears in the document header table."""
    institution_name: str = "Your Institution"
    department: str = "Department of English"
    regulation: str = ""
    logo_path: Optional[str] = None   # absolute path to .png / .jpg logo


@dataclass
class SectionConfig:
    """Defines one section (PART A, B, C …) of the exam paper."""
    part: str               # "A", "B", "C"
    label: str              # "PART A"
    title: str              # "Multiple Choice Questions"
    instruction: str        # "Answer all questions"
    question_type: str      # "mcq" | "short_answer" | "long_answer" | "case_study"
    either_or: bool         # True → pairs as N(a)/(OR)/N(b)
    marks_per_q: float      # marks per individual question (or per pair for either-or)
    difficulty_counts: dict = field(default_factory=lambda: {"easy": 0, "medium": 0, "hard": 0})
    # ^^^ e.g. {"easy": 10, "medium": 8, "hard": 2}

    @property
    def total_questions(self) -> int:
        return sum(self.difficulty_counts.values())

    @property
    def total_marks(self) -> float:
        if self.either_or:
            # Each pair (a+b) counts as one question slot
            pairs = self.total_questions // 2
            return pairs * self.marks_per_q
        return self.total_questions * self.marks_per_q


# ---------------------------------------------------------------------------
# Root config
# ---------------------------------------------------------------------------

@dataclass
class CourseConfig:
    """All settings needed to auto-generate an exam paper for one course."""
    course_code: str                          # "ENG101"
    course_name: str                          # "English Grammar"
    topic: str                                # matches `topic` column in CSV
    subtopic: str                             # matches `subtopic` column in CSV
    branding: BrandingConfig = field(default_factory=BrandingConfig)
    sections: list[SectionConfig] = field(default_factory=list)
    exam_title: str = "ANNUAL EXAMINATION"
    time_allowed: str = "3 Hours"
    watch_folder: str = ""    # stored as str for JSON serialisation; convert to Path on load
    output_folder: str = ""

    # ------------------------------------------------------------------ #
    # Computed helpers                                                     #
    # ------------------------------------------------------------------ #

    @property
    def grand_total_marks(self) -> float:
        return sum(s.total_marks for s in self.sections)

    # ------------------------------------------------------------------ #
    # Serialisation                                                        #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        d = asdict(self)
        # asdict handles nested dataclasses automatically
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "CourseConfig":
        branding = BrandingConfig(**data.get("branding", {}))
        sections = [SectionConfig(**s) for s in data.get("sections", [])]
        return cls(
            course_code=data.get("course_code", ""),
            course_name=data.get("course_name", ""),
            topic=data.get("topic", ""),
            subtopic=data.get("subtopic", ""),
            branding=branding,
            sections=sections,
            exam_title=data.get("exam_title", "ANNUAL EXAMINATION"),
            time_allowed=data.get("time_allowed", "3 Hours"),
            watch_folder=data.get("watch_folder", ""),
            output_folder=data.get("output_folder", ""),
        )

    def save(self, path: Path) -> None:
        """Write this config as JSON to *path*."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> "CourseConfig":
        """Load a CourseConfig from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    # ------------------------------------------------------------------ #
    # Convenience                                                          #
    # ------------------------------------------------------------------ #

    def get_section(self, part: str) -> Optional[SectionConfig]:
        """Return the SectionConfig for a given part letter (e.g. 'A')."""
        for s in self.sections:
            if s.part.upper() == part.upper():
                return s
        return None


# ---------------------------------------------------------------------------
# Default factory — creates a sensible 3-section English exam config
# ---------------------------------------------------------------------------

def default_english_config(
    course_code: str = "ENG101",
    watch_root: Path = Path("watch"),
) -> CourseConfig:
    """Return a ready-to-use ENG101 config with PART A/B/C for English Grammar."""
    watch_folder = watch_root / course_code
    output_folder = watch_folder / "output"
    return CourseConfig(
        course_code=course_code,
        course_name="English Grammar",
        topic="English Grammar",
        subtopic="Tenses",
        branding=BrandingConfig(
            institution_name="Your Institution",
            department="Department of English",
            regulation="2021 Regulation",
        ),
        sections=[
            SectionConfig(
                part="A",
                label="PART A",
                title="Multiple Choice Questions",
                instruction="Answer all the Questions",
                question_type="mcq",
                either_or=False,
                marks_per_q=1,
                difficulty_counts={"easy": 5, "medium": 5, "hard": 5},
            ),
            SectionConfig(
                part="B",
                label="PART B",
                title="Detailed Answer Type Questions (Either or choice)",
                instruction="Answer all the Questions",
                question_type="long_answer",
                either_or=True,
                marks_per_q=14,
                difficulty_counts={"easy": 2, "medium": 4, "hard": 4},
            ),
            SectionConfig(
                part="C",
                label="PART C",
                title="Application / Analysis / Case Study Type Question",
                instruction="Answer the Question",
                question_type="long_answer",
                either_or=False,
                marks_per_q=10,
                difficulty_counts={"easy": 0, "medium": 0, "hard": 1},
            ),
        ],
        exam_title="ANNUAL EXAMINATION",
        time_allowed="3 Hours",
        watch_folder=str(watch_folder),
        output_folder=str(output_folder),
    )

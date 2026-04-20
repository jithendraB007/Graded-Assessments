"""dataset_loader.py — Load, validate, and normalise the question dataset (CSV or Excel)."""
from __future__ import annotations

import io
from dataclasses import dataclass, field

import pandas as pd


# ---------------------------------------------------------------------------
# Normalisation maps
# ---------------------------------------------------------------------------

DIFFICULTY_NORMALISE: dict[str, str] = {
    "easy": "easy",
    "medium": "medium",
    "hard": "hard",
    "e": "easy",
    "m": "medium",
    "h": "hard",
    "simple": "easy",
    "moderate": "medium",
    "difficult": "hard",
    "low": "easy",
    "high": "hard",
}

TYPE_NORMALISE: dict[str, str] = {
    "mcq": "mcq",
    "multiple choice": "mcq",
    "multiple_choice": "mcq",
    "multiplechoice": "mcq",
    "short answer": "short_answer",
    "short_answer": "short_answer",
    "short": "short_answer",
    "sa": "short_answer",
    "long answer": "long_answer",
    "long_answer": "long_answer",
    "long": "long_answer",
    "la": "long_answer",
    "essay": "long_answer",
    "descriptive": "long_answer",
}

REQUIRED_COLUMNS = {
    "question_id",
    "topic",
    "subtopic",
    "difficulty",
    "question_type",
    "question_text",
}

MCQ_OPTION_COLS = ["option_a", "option_b", "option_c", "option_d"]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class DatasetResult:
    df: pd.DataFrame
    warnings: list[str] = field(default_factory=list)
    row_count: int = 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_dataset(file_buffer: io.BytesIO, filename: str) -> DatasetResult:
    """Load and validate a CSV or Excel question dataset.

    Args:
        file_buffer: BytesIO-compatible buffer (Streamlit UploadedFile works directly).
        filename:    Original filename — used to detect the file extension.

    Returns:
        DatasetResult with a clean DataFrame, any warnings, and the row count.

    Raises:
        ValueError: If the file format is unsupported or required columns are missing.
    """
    warnings: list[str] = []
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "csv":
        df = pd.read_csv(file_buffer)
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(file_buffer, engine="openpyxl")
    else:
        raise ValueError(
            f"Unsupported file type: .{ext}. Please upload a .csv or .xlsx file."
        )

    # --- Normalise column names ---
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)

    # --- Check required columns ---
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing)}. "
            f"Found columns: {sorted(df.columns.tolist())}"
        )

    # --- Ensure optional columns exist ---
    for col in MCQ_OPTION_COLS:
        if col not in df.columns:
            df[col] = ""
    if "correct_answer" not in df.columns:
        df["correct_answer"] = ""
    if "marks" not in df.columns:
        df["marks"] = ""
    if "btl" not in df.columns:
        df["btl"] = ""
    if "co" not in df.columns:
        df["co"] = ""

    # --- Normalise difficulty ---
    df["_difficulty_norm"] = df["difficulty"].apply(
        lambda v: DIFFICULTY_NORMALISE.get(str(v).strip().lower()) if pd.notna(v) else None
    )
    bad_diff = df[df["_difficulty_norm"].isna()]
    if not bad_diff.empty:
        bad_vals = bad_diff["difficulty"].unique().tolist()
        warnings.append(
            f"{len(bad_diff)} row(s) have unrecognised difficulty value(s) {bad_vals} "
            f"and will be skipped."
        )
    df = df[df["_difficulty_norm"].notna()].copy()
    df["difficulty"] = df["_difficulty_norm"]
    df.drop(columns=["_difficulty_norm"], inplace=True)

    # --- Normalise question_type ---
    df["_type_norm"] = df["question_type"].apply(
        lambda v: TYPE_NORMALISE.get(str(v).strip().lower()) if pd.notna(v) else None
    )
    bad_type = df[df["_type_norm"].isna()]
    if not bad_type.empty:
        bad_vals = bad_type["question_type"].unique().tolist()
        warnings.append(
            f"{len(bad_type)} row(s) have unrecognised question_type value(s) {bad_vals} "
            f"and will be skipped."
        )
    df = df[df["_type_norm"].notna()].copy()
    df["question_type"] = df["_type_norm"]
    df.drop(columns=["_type_norm"], inplace=True)

    # --- Validate MCQ option columns ---
    mcq_mask = df["question_type"] == "mcq"
    for col in MCQ_OPTION_COLS:
        missing_opts = df[
            mcq_mask & (df[col].isna() | (df[col].astype(str).str.strip() == ""))
        ]
        if not missing_opts.empty:
            warnings.append(
                f"{len(missing_opts)} MCQ row(s) are missing '{col}'. "
                f"They will render as '[option not provided]'."
            )

    # --- Deduplicate on question_id ---
    dupes = df[df.duplicated("question_id", keep="first")]
    if not dupes.empty:
        warnings.append(
            f"{len(dupes)} duplicate question_id(s) found; keeping first occurrence: "
            f"{dupes['question_id'].tolist()}"
        )
        df = df.drop_duplicates("question_id", keep="first")

    df = df.reset_index(drop=True)
    return DatasetResult(df=df, warnings=warnings, row_count=len(df))


def get_questions(
    df: pd.DataFrame,
    topic: str,
    subtopic: str,
    difficulty: str,
    question_type: str,
) -> pd.DataFrame:
    """Filter the dataset by topic, subtopic, difficulty, and question type.

    Matching is case-insensitive. Returns a shuffled DataFrame so repeated
    calls produce different orderings without needing external randomisation.
    """
    mask = (
        (df["topic"].str.strip().str.lower() == topic.strip().lower())
        & (df["subtopic"].str.strip().str.lower() == subtopic.strip().lower())
        & (df["difficulty"] == difficulty.strip().lower())
        & (df["question_type"] == question_type.strip().lower())
    )
    return df[mask].sample(frac=1).reset_index(drop=True)

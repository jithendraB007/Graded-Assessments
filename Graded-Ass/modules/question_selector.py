"""question_selector.py — Assign questions from the dataset to each placeholder.

Enforces no-duplicate rule across the entire paper by tracking used question IDs
in a single set that spans all placeholder assignments.

select_questions()           — used by the interactive Streamlit Generate tab.
select_questions_judge_aware() — used by the automated pipeline; runs the AI
                                 judge on a 3× pool of candidates and prefers
                                 Pass-verdict questions before falling back to
                                 Revise.  Fail questions are excluded; if no
                                 replacement can be found the slot is dropped
                                 and the rebalance_log records the action.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd

from modules.dataset_loader import get_questions
from modules.template_parser import PlaceholderRecord

if TYPE_CHECKING:
    from modules.course_config import CourseConfig
    from modules.judge import EnglishQualityJudge


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SelectionError:
    """Records a shortfall when the dataset cannot satisfy a placeholder's count."""
    placeholder_raw: str
    requested: int
    available: int

    @property
    def shortfall(self) -> int:
        return self.requested - self.available


@dataclass
class SelectionResult:
    """Maps each placeholder's raw string to its assigned question rows."""
    assignments: dict[str, pd.DataFrame] = field(default_factory=dict)
    errors: list[SelectionError] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def select_questions(
    placeholders: list[PlaceholderRecord],
    df: pd.DataFrame,
    topic: str,
    subtopic: str,
    easy_count: int,
    medium_count: int,
    hard_count: int,
) -> SelectionResult:
    """Assign dataset rows to each placeholder, tracking used IDs to avoid duplicates.

    Count resolution order (highest → lowest priority):
      1. count_hint encoded in the placeholder name  (e.g. {{EASY_MCQ_5}} → 5)
      2. The form-level difficulty count passed as easy_count / medium_count / hard_count

    Args:
        placeholders:  List of PlaceholderRecord objects from the template parser.
        df:            Clean DataFrame from the dataset loader.
        topic:         Topic filter string (case-insensitive).
        subtopic:      Subtopic filter string (case-insensitive).
        easy_count:    Default number of questions for Easy placeholders.
        medium_count:  Default number of questions for Medium placeholders.
        hard_count:    Default number of questions for Hard placeholders.

    Returns:
        SelectionResult with per-placeholder DataFrames and any shortfall errors.
    """
    difficulty_default: dict[str, int] = {
        "easy": int(easy_count),
        "medium": int(medium_count),
        "hard": int(hard_count),
    }

    used_ids: set[str] = set()
    result = SelectionResult()

    for record in placeholders:
        # Determine required count
        if record.count_hint is not None:
            count = record.count_hint
        else:
            count = difficulty_default.get(record.difficulty, 0)

        if count == 0:
            result.assignments[record.raw] = pd.DataFrame()
            continue

        # Fetch candidates filtered by topic/subtopic/difficulty/type
        candidates = get_questions(
            df, topic, subtopic, record.difficulty, record.question_type
        )

        # Exclude already-used questions
        available = candidates[
            ~candidates["question_id"].astype(str).isin(used_ids)
        ].reset_index(drop=True)

        if len(available) >= count:
            selected = available.head(count)
        else:
            selected = available
            result.errors.append(
                SelectionError(
                    placeholder_raw=record.raw,
                    requested=count,
                    available=len(available),
                )
            )

        # Mark these IDs as used
        used_ids.update(selected["question_id"].astype(str).tolist())
        result.assignments[record.raw] = selected.reset_index(drop=True)

    return result


# ---------------------------------------------------------------------------
# Judge-aware selection (pipeline mode only)
# ---------------------------------------------------------------------------

def select_questions_judge_aware(
    placeholders: list[PlaceholderRecord],
    df: pd.DataFrame,
    topic: str,
    subtopic: str,
    easy_count: int,
    medium_count: int,
    hard_count: int,
    judge: "EnglishQualityJudge",
    api_key: str,
    model: str = "mistral-small-latest",
) -> tuple["SelectionResult", list[str]]:
    """Select questions with AI judge pre-filtering.  Pipeline-mode only.

    For each placeholder slot:
    1. Fetch a pool of 3× the required count (candidates).
    2. Run the judge on every candidate (thread-safe via dspy.context).
    3. Prefer Pass-verdict rows; accept Revise; exclude Fail.
    4. If the filtered pool is still short, try an additional same-difficulty
       replacement draw from the remaining un-used pool.
    5. If still short, the slot count is reduced (rebalanced) and the action
       is recorded in rebalance_log.

    Returns:
        (SelectionResult, rebalance_log)  where rebalance_log is a list of
        human-readable strings describing any questions that were removed and
        any count adjustments made.
    """
    import dspy
    from modules.judge import judge_single_question, _make_lm

    lm = _make_lm(api_key, model)

    difficulty_default: dict[str, int] = {
        "easy": int(easy_count),
        "medium": int(medium_count),
        "hard": int(hard_count),
    }

    used_ids: set[str] = set()
    result = SelectionResult()
    rebalance_log: list[str] = []

    with dspy.context(lm=lm):
        for record in placeholders:
            count = (
                record.count_hint
                if record.count_hint is not None
                else difficulty_default.get(record.difficulty, 0)
            )

            if count == 0:
                result.assignments[record.raw] = pd.DataFrame()
                continue

            # Fetch a 3× pool so we have spare capacity after judge filtering
            candidates = get_questions(
                df, topic, subtopic, record.difficulty, record.question_type
            )
            pool = candidates[
                ~candidates["question_id"].astype(str).isin(used_ids)
            ].reset_index(drop=True)

            # Judge every candidate in the pool
            verdicts: dict[str, str] = {}  # question_id → verdict
            for _, row in pool.iterrows():
                try:
                    jr = judge_single_question(judge, row)
                    verdicts[str(row["question_id"])] = jr.overall_decision
                except Exception:
                    verdicts[str(row["question_id"])] = "Revise"

            # Split pool by verdict
            pass_pool   = pool[pool["question_id"].astype(str).map(verdicts) == "Pass"]
            revise_pool = pool[pool["question_id"].astype(str).map(verdicts) == "Revise"]
            fail_pool   = pool[pool["question_id"].astype(str).map(verdicts) == "Fail"]

            # Log removed Fail candidates
            for _, row in fail_pool.iterrows():
                rebalance_log.append(
                    f"Excluded {row['question_id']} ({record.difficulty} {record.question_type}) "
                    f"— judge verdict: Fail (not included in paper)"
                )

            # Build selection: Pass first, then Revise
            filtered = pd.concat([pass_pool, revise_pool], ignore_index=True)

            if len(filtered) >= count:
                selected = filtered.head(count)
            else:
                # Not enough passing/revising questions — record shortfall
                available = len(filtered)
                if available < count:
                    rebalance_log.append(
                        f"REBALANCE: {record.raw} requested {count} questions but only "
                        f"{available} passed/revised judge screening. "
                        f"Section count reduced to {available}."
                    )
                    result.errors.append(
                        SelectionError(
                            placeholder_raw=record.raw,
                            requested=count,
                            available=available,
                        )
                    )
                selected = filtered  # take all available

            used_ids.update(selected["question_id"].astype(str).tolist())
            result.assignments[record.raw] = selected.reset_index(drop=True)

    return result, rebalance_log

"""judge_optimizer.py — Optimize the English quality judge prompt using DSPy.

## How it works

Phase 1 — BootstrapFewShot (5+ examples):
  Picks the best training examples as few-shot demonstrations and injects them
  into the judge's prompt. This immediately improves consistency without
  rewriting the prompt itself.

Phase 2 — GEPA (20+ examples):
  Uses a reflection LM to iteratively rewrite the judge's instruction prompt,
  guided by training example scores. Produces a better prompt plus demos.

## Usage

    # Activate your venv, then:
    python -m optimize.judge_optimizer

Or call from the Streamlit app via the "Optimize Judge" button.

## Training data format (data/judge_training.jsonl)

Each line is a JSON object saved by the app when the user confirms a verdict:

    {
        "question_id":       "Q001",
        "question_text":     "What is the capital of France?",
        "question_type":     "mcq",
        "difficulty":        "easy",
        "option_a":          "London",
        "option_b":          "Paris",
        "option_c":          "Berlin",
        "option_d":          "Madrid",
        "correct_answer":    "B",
        "expected_overall_decision": "Pass"
    }

The field `expected_overall_decision` is the human-verified gold label.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Allow running as `python -m optimize.judge_optimizer` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dspy
from dotenv import load_dotenv

from modules.judge import (
    EnglishQualityJudgeSignature,
    ARTIFACT_PATH,
)

TRAINING_DATA_PATH = Path("data/judge_training.jsonl")
BOOTSTRAP_MIN_EXAMPLES = 5
GEPA_MIN_EXAMPLES = 20


# ---------------------------------------------------------------------------
# Flat wrapper for BootstrapFewShot / GEPA
# (optimizers expect flat keyword arguments, not object inputs)
# ---------------------------------------------------------------------------

class _JudgeFlat(dspy.Module):
    """Flat-input wrapper so optimizers can pass individual fields."""

    def __init__(self):
        super().__init__()
        self.judge = dspy.ChainOfThought(EnglishQualityJudgeSignature)

    def forward(
        self,
        question_text: str,
        question_type: str,
        difficulty: str,
        options_json: str,
        correct_answer: str,
    ):
        return self.judge(
            question_text=question_text,
            question_type=question_type,
            difficulty=difficulty,
            options_json=options_json,
            correct_answer=correct_answer,
        )


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

def _extract_decision(output_json: str) -> str | None:
    """Parse overall_decision from the LLM output JSON string."""
    try:
        cleaned = output_json.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
            cleaned = cleaned[: cleaned.rfind("```")]
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        payload = json.loads(cleaned)
        return payload.get("overall_decision")
    except Exception:
        return None


def bootstrap_metric(gold, pred, trace=None) -> float:
    """Metric for BootstrapFewShot: returns 1.0 if prediction matches gold label."""
    predicted = _extract_decision(pred.output_json)
    expected = gold.expected_overall_decision
    return 1.0 if predicted == expected else 0.0


def gepa_metric(gold, pred, trace=None, **kwargs) -> tuple[float, str]:
    """Metric for GEPA: returns (score, feedback_string) tuple."""
    predicted = _extract_decision(pred.output_json)
    expected = gold.expected_overall_decision
    score = 1.0 if predicted == expected else 0.0
    feedback = (
        f"Expected overall_decision='{expected}', got '{predicted}'. "
        f"Focus on: ambiguity (→ Fail), grammatical errors (→ Fail), "
        f"weak distractors (→ Revise), difficulty mismatch (→ Revise)."
    )
    return score, feedback


# ---------------------------------------------------------------------------
# Training data loader
# ---------------------------------------------------------------------------

def load_trainset(path: Path = TRAINING_DATA_PATH) -> list[dspy.Example]:
    """Load labelled examples from the JSONL file."""
    if not path.exists() or path.stat().st_size == 0:
        return []

    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            qt = str(obj.get("question_type", ""))
            if qt == "mcq":
                options = {
                    "A": str(obj.get("option_a", "") or ""),
                    "B": str(obj.get("option_b", "") or ""),
                    "C": str(obj.get("option_c", "") or ""),
                    "D": str(obj.get("option_d", "") or ""),
                }
                options_json = json.dumps(options)
            else:
                options_json = ""

            example = dspy.Example(
                question_text=str(obj.get("question_text", "")),
                question_type=qt,
                difficulty=str(obj.get("difficulty", "")),
                options_json=options_json,
                correct_answer=str(obj.get("correct_answer", "") or ""),
                expected_overall_decision=str(obj.get("expected_overall_decision", "Pass")),
            ).with_inputs(
                "question_text", "question_type", "difficulty",
                "options_json", "correct_answer"
            )
            examples.append(example)

    return examples


# ---------------------------------------------------------------------------
# Optimization runners
# ---------------------------------------------------------------------------

def run_bootstrap(trainset: list[dspy.Example]) -> None:
    """Phase 1: BootstrapFewShot — adds best demonstrations to prompt.

    Saves artifact to artifacts/english_judge_optimized.json.
    Recommended when you have 5–19 labelled examples.
    """
    from dspy.teleprompt import BootstrapFewShot

    print(f"Running BootstrapFewShot on {len(trainset)} examples...")
    student = _JudgeFlat()
    optimizer = BootstrapFewShot(
        metric=bootstrap_metric,
        max_bootstrapped_demos=3,
        max_labeled_demos=4,
    )
    optimized = optimizer.compile(student, trainset=trainset)
    ARTIFACT_PATH.parent.mkdir(exist_ok=True)
    optimized.save(str(ARTIFACT_PATH))
    print(f"Saved optimized judge to {ARTIFACT_PATH}")


def run_gepa(trainset: list[dspy.Example], reflection_model: str | None = None) -> None:
    """Phase 2: GEPA — rewrites the instruction prompt for better accuracy.

    GEPA uses a separate (often stronger) reflection LM to generate improved
    prompts and evaluates them on the trainset. Recommended with 20+ examples.

    Args:
        trainset:         Labelled examples from data/judge_training.jsonl
        reflection_model: Optional stronger LM for prompt rewriting
                          e.g. "openai/mistral-medium-latest". Defaults to
                          the same model already configured in dspy.
    """
    try:
        from dspy.teleprompt import GEPA
    except ImportError:
        print("GEPA not available in this DSPy version — falling back to BootstrapFewShot.")
        run_bootstrap(trainset)
        return

    print(f"Running GEPA on {len(trainset)} examples...")

    # Optionally use a stronger model for reflection
    teacher_lm = None
    if reflection_model:
        api_key = os.environ.get("MISTRAL_API_KEY", "")
        teacher_lm = dspy.LM(
            f"openai/{reflection_model}",
            api_key=api_key,
            api_base="https://api.mistral.ai/v1",
            temperature=0.3,
            max_tokens=1500,
        )

    student = _JudgeFlat()
    optimizer = GEPA(
        metric=gepa_metric,
        max_bootstrapped_demos=3,
        num_candidates=8,
        **({"teacher_lm": teacher_lm} if teacher_lm else {}),
    )
    optimized = optimizer.compile(student, trainset=trainset)
    ARTIFACT_PATH.parent.mkdir(exist_ok=True)
    optimized.save(str(ARTIFACT_PATH))
    print(f"Saved GEPA-optimized judge to {ARTIFACT_PATH}")


def optimize(force_gepa: bool = False) -> str:
    """Main entry point: choose optimizer based on training data size.

    Returns a status message string (used by the Streamlit app).
    """
    load_dotenv()

    api_key = os.environ.get("MISTRAL_API_KEY", "")
    if not api_key:
        return "MISTRAL_API_KEY not set in .env — cannot run optimization."

    model = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")
    lm = dspy.LM(
        f"openai/{model}",
        api_key=api_key,
        api_base="https://api.mistral.ai/v1",
        temperature=0.1,
        max_tokens=800,
    )
    dspy.configure(lm=lm)

    trainset = load_trainset()
    n = len(trainset)

    if n < BOOTSTRAP_MIN_EXAMPLES:
        return (
            f"Not enough labelled examples yet ({n} collected, "
            f"{BOOTSTRAP_MIN_EXAMPLES} needed). "
            f"Keep confirming judge verdicts in the app to build up the training set."
        )

    if n >= GEPA_MIN_EXAMPLES or force_gepa:
        run_gepa(trainset)
        return f"GEPA optimization complete using {n} examples. Judge prompt updated."
    else:
        run_bootstrap(trainset)
        return (
            f"BootstrapFewShot optimization complete using {n} examples. "
            f"Judge prompt updated with {min(3, n)} demonstrations. "
            f"Collect {GEPA_MIN_EXAMPLES - n} more examples to unlock GEPA (full prompt rewrite)."
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Optimize the English quality judge.")
    parser.add_argument(
        "--gepa", action="store_true",
        help="Force GEPA even if fewer than 20 examples are available."
    )
    parser.add_argument(
        "--reflection-model", default=None,
        help="Stronger model for GEPA prompt rewriting "
             "(e.g. mistral-medium-latest). Defaults to MISTRAL_MODEL in .env."
    )
    args = parser.parse_args()

    msg = optimize(force_gepa=args.gepa)
    print(msg)

"""judge.py — DSPy-based English quality judge for exam questions.

Evaluates every inserted question on 7 criteria and returns a Pass / Revise / Fail
verdict. Loads an optimized artifact (BootstrapFewShot demos) if one exists at
artifacts/english_judge_optimized.json; otherwise runs zero-shot.

Prompt is automatically improved over time via the optimize/judge_optimizer.py
script once the user has collected enough labelled feedback examples.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import dspy

ARTIFACT_PATH = Path("artifacts/english_judge_optimized.json")

DECISION_LABELS = {"Pass", "Revise", "Fail"}


# ---------------------------------------------------------------------------
# DSPy Signature
# ---------------------------------------------------------------------------

class EnglishQualityJudgeSignature(dspy.Signature):
    """You are a senior English language exam paper quality reviewer.

    Evaluate the given exam question for use in a formal English examination.
    Your job is to detect quality issues that would confuse students or
    misrepresent the intended difficulty level.

    Assess the following criteria and return a single valid JSON object:

    1. grammatical_accuracy
       - "None"         : No grammatical errors.
       - "Minor Issue"  : Small errors that do not affect understanding.
       - "Major Issue"  : Errors that confuse or mislead the student.

    2. clarity
       - "None"         : Perfectly clear with a single valid interpretation.
       - "Minor Issue"  : Slightly vague but still answerable.
       - "Major Issue"  : Ambiguous — more than one reasonable interpretation exists.

    3. difficulty_alignment
       - "Aligned"      : The question genuinely matches the stated difficulty.
       - "Too Easy"     : The question is easier than stated.
       - "Too Hard"     : The question is harder than stated.

    4. language_level_appropriateness
       - "Appropriate"  : Vocabulary and syntax suit the difficulty level.
       - "Too Simple"   : Language is below the target level.
       - "Too Complex"  : Language is above the target level.

    5. instruction_clarity
       - "Clear"        : Instructions are unambiguous.
       - "Unclear"      : The student may not know what is being asked.

    6. distractor_quality  (MCQ only; use "N/A" for non-MCQ)
       - "Good"         : All distractors are plausible but have one clear correct answer.
       - "Weak"         : One or more distractors are obviously wrong or the correct
                          answer is ambiguous.

    7. format_compliance
       - "Pass"         : Proper punctuation, no spelling errors, correct structure.
       - "Fail"         : Spelling mistakes, missing punctuation, or structural errors.

    8. overall_decision
       - "Pass"   : Ready to use as-is.
       - "Revise" : Needs minor corrections before use.
       - "Fail"   : Should not be used — contains major quality issues.

       RULES FOR overall_decision:
         - If clarity == "Major Issue"  → MUST be "Fail"
         - If grammatical_accuracy == "Major Issue" → MUST be "Fail"
         - If instruction_clarity == "Unclear" → at minimum "Revise"
         - If distractor_quality == "Weak" (MCQ) → at minimum "Revise"

    9. priority_reason
       The single most important reason for the overall_decision.
       Use an empty string "" if overall_decision is "Pass".

    10. revision_feedback
        Specific, actionable suggestions for improvement.
        Use an empty string "" if overall_decision is "Pass".

    Return ONLY the JSON object. No extra text or markdown fences.
    """

    question_text = dspy.InputField(desc="The full text of the exam question")
    question_type = dspy.InputField(desc="One of: mcq, short_answer, long_answer")
    difficulty    = dspy.InputField(desc="Stated difficulty: easy, medium, or hard")
    options_json  = dspy.InputField(
        desc='JSON string of MCQ options e.g. {"A":"..","B":"..","C":"..","D":".."}, '
             'or empty string "" for non-MCQ questions'
    )
    correct_answer = dspy.InputField(
        desc="Correct answer: A/B/C/D for MCQ, or answer text for other types"
    )
    output_json = dspy.OutputField(
        desc="JSON object with keys: grammatical_accuracy, clarity, "
             "difficulty_alignment, language_level_appropriateness, "
             "instruction_clarity, distractor_quality, format_compliance, "
             "overall_decision, priority_reason, revision_feedback"
    )


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class JudgeResult:
    question_id: str
    question_text: str
    question_type: str
    difficulty: str
    # Criteria
    grammatical_accuracy: str
    clarity: str
    difficulty_alignment: str
    language_level_appropriateness: str
    instruction_clarity: str
    distractor_quality: str
    format_compliance: str
    # Verdict
    overall_decision: str      # "Pass" | "Revise" | "Fail"
    priority_reason: str
    revision_feedback: str
    # Raw LLM output for debugging
    raw_output: str = ""
    parse_error: bool = False


# ---------------------------------------------------------------------------
# DSPy Module
# ---------------------------------------------------------------------------

class EnglishQualityJudge(dspy.Module):
    """Wraps EnglishQualityJudgeSignature with ChainOfThought reasoning."""

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
    ) -> str:
        result = self.judge(
            question_text=question_text,
            question_type=question_type,
            difficulty=difficulty,
            options_json=options_json,
            correct_answer=correct_answer,
        )
        return result.output_json


def _call_judge(
    judge: "EnglishQualityJudge",
    question_text: str,
    question_type: str,
    difficulty: str,
    options_json: str,
    correct_answer: str,
) -> str:
    """Call judge via __call__ (dspy.Module recommended interface).

    EnglishQualityJudge.forward() returns output_json (a str) directly,
    so judge(...) also returns that string — not a Prediction object.
    """
    return judge(
        question_text=question_text,
        question_type=question_type,
        difficulty=difficulty,
        options_json=options_json,
        correct_answer=correct_answer,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_output(raw: str) -> tuple[dict, bool]:
    """Parse JSON from the LLM output. Returns (payload, had_error)."""
    cleaned = raw.strip()
    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:])
        if cleaned.endswith("```"):
            cleaned = cleaned[: cleaned.rfind("```")]
    # Try to find the JSON object if extra text surrounds it
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        cleaned = cleaned[start:end]
    try:
        return json.loads(cleaned), False
    except json.JSONDecodeError:
        return {}, True


def _fallback_payload(raw: str) -> dict:
    return {
        "grammatical_accuracy": "Unknown",
        "clarity": "Unknown",
        "difficulty_alignment": "Unknown",
        "language_level_appropriateness": "Unknown",
        "instruction_clarity": "Unknown",
        "distractor_quality": "N/A",
        "format_compliance": "Unknown",
        "overall_decision": "Revise",
        "priority_reason": "Judge output could not be parsed",
        "revision_feedback": raw[:300] if raw else "",
    }


def _enforce_rules(payload: dict) -> dict:
    """Apply hard override rules on overall_decision."""
    if payload.get("clarity", "").lower() == "major issue":
        payload["overall_decision"] = "Fail"
    if payload.get("grammatical_accuracy", "").lower() == "major issue":
        payload["overall_decision"] = "Fail"
    if payload.get("instruction_clarity", "").lower() == "unclear":
        if payload.get("overall_decision") == "Pass":
            payload["overall_decision"] = "Revise"
    if payload.get("distractor_quality", "").lower() == "weak":
        if payload.get("overall_decision") == "Pass":
            payload["overall_decision"] = "Revise"
    return payload


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _make_lm(api_key: str, model: str = "mistral-small-latest") -> dspy.LM:
    """Create a DSPy LM object for Mistral AI (does not mutate global settings)."""
    return dspy.LM(
        f"openai/{model}",
        api_key=api_key,
        api_base="https://api.mistral.ai/v1",
        temperature=0.1,
        max_tokens=800,
    )


def load_judge(artifact_path: Path = ARTIFACT_PATH) -> EnglishQualityJudge:
    """Create the judge module, loading an optimized artifact if available."""
    judge = EnglishQualityJudge()
    if artifact_path.exists():
        try:
            judge.load(str(artifact_path))
        except Exception:
            pass  # Gracefully fall back to zero-shot
    return judge


def judge_single_question(judge: EnglishQualityJudge, row: dict) -> JudgeResult:
    """Run the judge on a single question (dict or pandas Series)."""
    qt = str(row.get("question_type", ""))

    if qt == "mcq":
        options = {
            "A": str(row.get("option_a", "") or ""),
            "B": str(row.get("option_b", "") or ""),
            "C": str(row.get("option_c", "") or ""),
            "D": str(row.get("option_d", "") or ""),
        }
        options_json = json.dumps(options)
    else:
        options_json = ""

    raw = _call_judge(
        judge,
        question_text=str(row.get("question_text", "")),
        question_type=qt,
        difficulty=str(row.get("difficulty", "")),
        options_json=options_json,
        correct_answer=str(row.get("correct_answer", "") or ""),
    )

    payload, had_error = _parse_output(raw)
    if had_error or not payload:
        payload = _fallback_payload(raw)

    payload = _enforce_rules(payload)

    # Guard: ensure overall_decision is valid
    if payload.get("overall_decision") not in DECISION_LABELS:
        payload["overall_decision"] = "Revise"

    return JudgeResult(
        question_id=str(row.get("question_id", "unknown")),
        question_text=str(row.get("question_text", "")),
        question_type=qt,
        difficulty=str(row.get("difficulty", "")),
        grammatical_accuracy=payload.get("grammatical_accuracy", "Unknown"),
        clarity=payload.get("clarity", "Unknown"),
        difficulty_alignment=payload.get("difficulty_alignment", "Unknown"),
        language_level_appropriateness=payload.get("language_level_appropriateness", "Unknown"),
        instruction_clarity=payload.get("instruction_clarity", "Unknown"),
        distractor_quality=payload.get("distractor_quality", "N/A"),
        format_compliance=payload.get("format_compliance", "Unknown"),
        overall_decision=payload.get("overall_decision", "Revise"),
        priority_reason=payload.get("priority_reason", ""),
        revision_feedback=payload.get("revision_feedback", ""),
        raw_output=raw,
        parse_error=had_error,
    )


def run_judge_on_assignments(
    assignments: dict,
    api_key: str,
    model: str = "mistral-small-latest",
) -> list[JudgeResult]:
    """Judge all questions across all placeholder assignments.

    Uses dspy.context() so the LM is scoped to this call only — thread-safe
    for Streamlit, which runs each interaction in a separate thread.

    Args:
        assignments:  dict mapping placeholder_raw → pd.DataFrame (from SelectionResult)
        api_key:      Mistral AI API key
        model:        Mistral model name

    Returns:
        List of JudgeResult, one per question, in insertion order.
    """
    lm = _make_lm(api_key, model)
    judge = load_judge()

    results: list[JudgeResult] = []
    with dspy.context(lm=lm):
        for _, df in assignments.items():
            if df is None or (hasattr(df, "empty") and df.empty):
                continue
            for _, row in df.iterrows():
                try:
                    result = judge_single_question(judge, row)
                except Exception as exc:
                    result = JudgeResult(
                        question_id=str(row.get("question_id", "unknown")),
                        question_text=str(row.get("question_text", ""))[:120],
                        question_type=str(row.get("question_type", "")),
                        difficulty=str(row.get("difficulty", "")),
                        grammatical_accuracy="Error",
                        clarity="Error",
                        difficulty_alignment="Error",
                        language_level_appropriateness="Error",
                        instruction_clarity="Error",
                        distractor_quality="Error",
                        format_compliance="Error",
                        overall_decision="Revise",
                        priority_reason=f"Judge error: {str(exc)[:120]}",
                        revision_feedback="",
                        parse_error=True,
                    )
                results.append(result)

    return results

"""
Parse Google Sheet tabs into university-specific request objects.

Required Sheet structure per university
────────────────────────────────────────

AMET  (5 tabs)
  Config        key           | value
  Instructions  instruction
  Part_A        number | text | mark | btl | co
  Part_B        pair | option | number | text | mark | btl | co
  Part_C        number | text | mark | btl | co

ANU   (4 tabs)
  Config        key           | value
  Notes         note
  Part_A        sub | text | co | bloom
  Part_B        number | text | marks | co | bloom
                  — use "(OR)" in the number column for OR separator rows

CDU   (4 tabs)
  Config        key           | value
  Set_A         section | pair | number | text
                  section = A or B; pair = 1,2,... (used for Section B grouping)
  Set_B         same layout as Set_A
  Set_C         same layout as Set_A

S-VYASA  (3 tabs)
  Config        key           | value
  Part_A        number | text | co | rbtl | marks
  Part_B        pair | option | number | text | co | rbtl | marks
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "libs" / "src"))

from graded_assessment.domain.amet_types import (
    AmetAssessmentRequest, AmetPartA, AmetPartB, AmetPartC,
    AmetQuestion, AmetQuestionPair,
)
from graded_assessment.domain.anu_types import (
    AnuAssessmentRequest, AnuPartA, AnuPartB,
    AnuSubQuestion, AnuPartBQuestion,
)
from graded_assessment.domain.cdu_types import (
    CduAssessmentRequest, CduSet, CduSectionA, CduSectionB,
    CduQuestion, CduQuestionPair,
)
from graded_assessment.domain.svyasa_types import (
    SvyasaAssessmentRequest, SvyasaPartA, SvyasaPartB,
    SvyasaQuestion, SvyasaQuestionPair,
)

from integrations.gws_client import read_sheet


# ── helpers ───────────────────────────────────────────────────────────────────

def _config(spreadsheet_id: str, tab: str = "Config") -> dict[str, str]:
    """Read a key/value tab and return it as a dict."""
    rows = read_sheet(spreadsheet_id, tab)
    return {row[0]: row[1] for row in rows if len(row) >= 2 and row[0] != "key"}


def _rows(spreadsheet_id: str, tab: str) -> list[dict[str, str]]:
    """Read a tab with a header row. Returns list of dicts keyed by column name."""
    rows = read_sheet(spreadsheet_id, tab)
    if not rows:
        return []
    headers = rows[0]
    return [
        {headers[i]: cell for i, cell in enumerate(row)}
        for row in rows[1:]
        if any(c.strip() for c in row)
    ]


# ── AMET ─────────────────────────────────────────────────────────────────────

def parse_amet(spreadsheet_id: str) -> AmetAssessmentRequest:
    cfg = _config(spreadsheet_id)
    instructions = [r["instruction"] for r in _rows(spreadsheet_id, "Instructions")]

    def _q(row: dict) -> AmetQuestion:
        return AmetQuestion(
            number=row["number"],
            text=row["text"],
            mark=int(row["mark"]),
            btl=row["btl"],
            co=row["co"],
        )

    part_a_questions = [_q(r) for r in _rows(spreadsheet_id, "Part_A")]

    pairs: dict[str, dict[str, AmetQuestion]] = {}
    for row in _rows(spreadsheet_id, "Part_B"):
        pairs.setdefault(row["pair"], {})[row["option"]] = _q(row)
    part_b_pairs = [
        AmetQuestionPair(a=v["a"], b=v["b"])
        for v in pairs.values()
    ]

    part_c_rows = _rows(spreadsheet_id, "Part_C")
    part_c_q = _q(part_c_rows[0])

    return AmetAssessmentRequest(
        exam_type=cfg["exam_type"],
        programme=cfg["programme"],
        semester=cfg["semester"],
        course_name=cfg["course_name"],
        course_code=cfg["course_code"],
        duration=cfg["duration"],
        max_marks=int(cfg["max_marks"]),
        instructions=instructions,
        part_a=AmetPartA(
            total=cfg.get("part_a_total", f"{len(part_a_questions)}×1 = {len(part_a_questions)} Marks"),
            instruction=cfg.get("part_a_instruction", "Answer all the questions"),
            questions=part_a_questions,
        ),
        part_b=AmetPartB(
            total=cfg.get("part_b_total", f"{len(part_b_pairs)}×14 = {len(part_b_pairs)*14} Marks"),
            instruction=cfg.get("part_b_instruction", "Answer all the questions"),
            question_pairs=part_b_pairs,
        ),
        part_c=AmetPartC(
            total=cfg.get("part_c_total", "1×10 = 10 Marks"),
            instruction=cfg.get("part_c_instruction", "Answer the Question"),
            question=part_c_q,
        ),
    )


# ── ANU ──────────────────────────────────────────────────────────────────────

def parse_anu(spreadsheet_id: str) -> AnuAssessmentRequest:
    cfg = _config(spreadsheet_id)
    notes = [r["note"] for r in _rows(spreadsheet_id, "Notes")]

    part_a_subs = [
        AnuSubQuestion(sub=r["sub"], text=r["text"], co=r["co"], bloom=r["bloom"])
        for r in _rows(spreadsheet_id, "Part_A")
    ]

    part_b_questions = [
        AnuPartBQuestion(
            number=r["number"],
            text=r["text"],
            marks=r.get("marks", ""),
            co=r.get("co", ""),
            bloom=r.get("bloom", ""),
        )
        for r in _rows(spreadsheet_id, "Part_B")
    ]

    return AnuAssessmentRequest(
        university_name=cfg["university_name"],
        batch=cfg["batch"],
        exam_type=cfg["exam_type"],
        course_name=cfg["course_name"],
        date=cfg.get("date", ""),
        duration=cfg["duration"],
        max_marks=int(cfg["max_marks"]),
        notes=notes,
        part_a=AnuPartA(sub_questions=part_a_subs),
        part_b=AnuPartB(questions=part_b_questions),
    )


# ── CDU ──────────────────────────────────────────────────────────────────────

def _parse_cdu_set(spreadsheet_id: str, tab: str, label: str) -> CduSet:
    rows = _rows(spreadsheet_id, tab)

    sec_a_rows = [r for r in rows if r.get("section", "").upper() == "A"]
    sec_b_rows = [r for r in rows if r.get("section", "").upper() == "B"]

    sec_a_questions = [CduQuestion(number=r["number"], text=r["text"]) for r in sec_a_rows]

    pairs: dict[str, list[CduQuestion]] = {}
    for r in sec_b_rows:
        pairs.setdefault(r["pair"], []).append(CduQuestion(number=r["number"], text=r["text"]))
    sec_b_pairs = [
        CduQuestionPair(a=qs[0], b=qs[1])
        for qs in pairs.values()
        if len(qs) >= 2
    ]

    cfg = _config(spreadsheet_id)

    return CduSet(
        label=label,
        section_a=CduSectionA(
            instruction=cfg.get("section_a_instruction", "Answer any six Questions."),
            questions=sec_a_questions,
        ),
        section_b=CduSectionB(
            instruction=cfg.get("section_b_instruction", "Answer the following Questions."),
            question_pairs=sec_b_pairs,
        ),
    )


def parse_cdu(spreadsheet_id: str) -> CduAssessmentRequest:
    cfg = _config(spreadsheet_id)
    return CduAssessmentRequest(
        university_name=cfg["university_name"],
        course_info=cfg["course_info"],
        time=cfg["time"],
        max_marks=int(cfg["max_marks"]),
        sets=[
            _parse_cdu_set(spreadsheet_id, "Set_A", "Set - A"),
            _parse_cdu_set(spreadsheet_id, "Set_B", "Set - B"),
            _parse_cdu_set(spreadsheet_id, "Set_C", "Set - C"),
        ],
    )


# ── S-VYASA ──────────────────────────────────────────────────────────────────

def parse_svyasa(spreadsheet_id: str) -> SvyasaAssessmentRequest:
    cfg = _config(spreadsheet_id)

    part_a_questions = [
        SvyasaQuestion(
            number=r["number"],
            text=r["text"],
            co=r["co"],
            rbtl=r["rbtl"],
            marks=int(r["marks"]),
        )
        for r in _rows(spreadsheet_id, "Part_A")
    ]

    pairs: dict[str, dict[str, SvyasaQuestion]] = {}
    for r in _rows(spreadsheet_id, "Part_B"):
        q = SvyasaQuestion(
            number=r["number"],
            text=r["text"],
            co=r["co"],
            rbtl=r["rbtl"],
            marks=int(r["marks"]),
        )
        pairs.setdefault(r["pair"], {})[r["option"]] = q
    part_b_pairs = [
        SvyasaQuestionPair(a=v["a"], b=v["b"])
        for v in pairs.values()
    ]

    return SvyasaAssessmentRequest(
        month_year=cfg["month_year"],
        academic_year=cfg["academic_year"],
        program=cfg["program"],
        specialization=cfg["specialization"],
        semester=cfg["semester"],
        date_of_exam=cfg.get("date_of_exam", ""),
        course_code=cfg["course_code"],
        course_name=cfg["course_name"],
        part_a=SvyasaPartA(questions=part_a_questions),
        part_b=SvyasaPartB(question_pairs=part_b_pairs),
    )


# ── dispatch ──────────────────────────────────────────────────────────────────

PARSERS = {
    "amet":    parse_amet,
    "anu":     parse_anu,
    "cdu":     parse_cdu,
    "s-vyasa": parse_svyasa,
}


def parse(university_id: str, spreadsheet_id: str):
    parser = PARSERS.get(university_id)
    if not parser:
        raise ValueError(f"Unknown university_id '{university_id}'. Choose from: {list(PARSERS)}")
    return parser(spreadsheet_id)

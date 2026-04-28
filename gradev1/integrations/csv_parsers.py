"""
Parse a university question CSV into a typed request object.

CSV format — one file, 8 columns:
    section, f1, f2, f3, f4, f5, f6, f7

Column meanings vary by section row:

  AMET
  ─────
  config        f1=key              f2=value
  instruction   f1=text
  part_a        f1=number  f2=text  f3=mark  f4=btl  f5=co
  part_b        f1=pair    f2=opt   f3=num   f4=text f5=mark f6=btl f7=co
  part_c        f1=number  f2=text  f3=mark  f4=btl  f5=co

  ANU
  ─────
  config        f1=key              f2=value
  note          f1=text
  part_a        f1=sub     f2=text  f3=co    f4=bloom
  part_b        f1=number  f2=text  f3=marks f4=co   f5=bloom
               (use number=(OR) for OR separator rows)

  CDU
  ─────
  config        f1=key              f2=value
  set_a_a       f1=number  f2=text           (Set A, Section A question)
  set_a_b       f1=pair    f2=number f3=text  (Set A, Section B pair row)
  set_b_a / set_b_b / set_c_a / set_c_b  — same pattern for Set B and Set C

  S-VYASA
  ────────
  config        f1=key              f2=value
  part_a        f1=number  f2=text  f3=co    f4=rbtl f5=marks
  part_b        f1=pair    f2=opt   f3=num   f4=text f5=co   f6=rbtl f7=marks
"""
from __future__ import annotations

import csv
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


def _read(csv_path: str) -> list[dict[str, str]]:
    rows = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip() or row[0].strip().startswith("#"):
                continue
            padded = (row + [""] * 8)[:8]
            rows.append({
                "section": padded[0].strip().lower(),
                "f1": padded[1].strip(),
                "f2": padded[2].strip(),
                "f3": padded[3].strip(),
                "f4": padded[4].strip(),
                "f5": padded[5].strip(),
                "f6": padded[6].strip(),
                "f7": padded[7].strip(),
            })
    return rows


# ── AMET ─────────────────────────────────────────────────────────────────────

def parse_amet_csv(csv_path: str) -> AmetAssessmentRequest:
    cfg, instructions, pa, pb, pc = {}, [], [], [], []
    for r in _read(csv_path):
        s = r["section"]
        if s == "config":
            cfg[r["f1"]] = r["f2"]
        elif s == "instruction":
            if r["f1"]:
                instructions.append(r["f1"])
        elif s == "part_a":
            pa.append(r)
        elif s == "part_b":
            pb.append(r)
        elif s == "part_c":
            pc.append(r)

    def _q(r, num="f1", txt="f2", mrk="f3", btl="f4", co="f5", default_mark=1):
        return AmetQuestion(
            number=r[num], text=r[txt],
            mark=int(r[mrk] or default_mark), btl=r[btl], co=r[co],
        )

    part_a_questions = [_q(r) for r in pa]

    pairs: dict[str, dict[str, AmetQuestion]] = {}
    for r in pb:
        q = AmetQuestion(
            number=r["f3"], text=r["f4"],
            mark=int(r["f5"] or 14), btl=r["f6"], co=r["f7"],
        )
        pairs.setdefault(r["f1"], {})[r["f2"]] = q
    part_b_pairs = [AmetQuestionPair(a=v["a"], b=v["b"]) for v in pairs.values()]

    part_c_q = _q(pc[0], default_mark=10)

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

def parse_anu_csv(csv_path: str) -> AnuAssessmentRequest:
    cfg, notes, pa, pb = {}, [], [], []
    for r in _read(csv_path):
        s = r["section"]
        if s == "config":
            cfg[r["f1"]] = r["f2"]
        elif s == "note":
            if r["f1"]:
                notes.append(r["f1"])
        elif s == "part_a":
            pa.append(r)
        elif s == "part_b":
            pb.append(r)

    part_a_subs = [
        AnuSubQuestion(sub=r["f1"], text=r["f2"], co=r["f3"], bloom=r["f4"])
        for r in pa
    ]
    part_b_questions = [
        AnuPartBQuestion(
            number=r["f1"], text=r["f2"],
            marks=r["f3"], co=r["f4"], bloom=r["f5"],
        )
        for r in pb
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

def _build_cdu_set(rows: list[dict], label: str, sec_a_instr: str, sec_b_instr: str) -> CduSet:
    sec_a = [CduQuestion(number=r["f1"], text=r["f2"]) for r in rows if r["section"].endswith("_a")]
    pb_rows = [r for r in rows if r["section"].endswith("_b")]
    pairs: dict[str, list[CduQuestion]] = {}
    for r in pb_rows:
        pairs.setdefault(r["f1"], []).append(CduQuestion(number=r["f2"], text=r["f3"]))
    sec_b_pairs = [CduQuestionPair(a=qs[0], b=qs[1]) for qs in pairs.values() if len(qs) >= 2]
    return CduSet(
        label=label,
        section_a=CduSectionA(instruction=sec_a_instr, questions=sec_a),
        section_b=CduSectionB(instruction=sec_b_instr, question_pairs=sec_b_pairs),
    )


def parse_cdu_csv(csv_path: str) -> CduAssessmentRequest:
    cfg = {}
    buckets: dict[str, list[dict]] = {
        "set_a_a": [], "set_a_b": [],
        "set_b_a": [], "set_b_b": [],
        "set_c_a": [], "set_c_b": [],
    }
    for r in _read(csv_path):
        s = r["section"]
        if s == "config":
            cfg[r["f1"]] = r["f2"]
        elif s in buckets:
            buckets[s].append(r)

    sec_a_instr = cfg.get("section_a_instruction", "Answer any six Questions.")
    sec_b_instr = cfg.get("section_b_instruction", "Answer the following Questions.")

    return CduAssessmentRequest(
        university_name=cfg["university_name"],
        course_info=cfg["course_info"],
        time=cfg["time"],
        max_marks=int(cfg["max_marks"]),
        sets=[
            _build_cdu_set(buckets["set_a_a"] + buckets["set_a_b"], "Set - A", sec_a_instr, sec_b_instr),
            _build_cdu_set(buckets["set_b_a"] + buckets["set_b_b"], "Set - B", sec_a_instr, sec_b_instr),
            _build_cdu_set(buckets["set_c_a"] + buckets["set_c_b"], "Set - C", sec_a_instr, sec_b_instr),
        ],
    )


# ── S-VYASA ──────────────────────────────────────────────────────────────────

def parse_svyasa_csv(csv_path: str) -> SvyasaAssessmentRequest:
    cfg, pa, pb = {}, [], []
    for r in _read(csv_path):
        s = r["section"]
        if s == "config":
            cfg[r["f1"]] = r["f2"]
        elif s == "part_a":
            pa.append(r)
        elif s == "part_b":
            pb.append(r)

    part_a_questions = [
        SvyasaQuestion(number=r["f1"], text=r["f2"], co=r["f3"], rbtl=r["f4"], marks=int(r["f5"] or 3))
        for r in pa
    ]

    pairs: dict[str, dict[str, SvyasaQuestion]] = {}
    for r in pb:
        q = SvyasaQuestion(
            number=r["f3"], text=r["f4"], co=r["f5"], rbtl=r["f6"], marks=int(r["f7"] or 14),
        )
        pairs.setdefault(r["f1"], {})[r["f2"]] = q
    part_b_pairs = [SvyasaQuestionPair(a=v["a"], b=v["b"]) for v in pairs.values()]

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

CSV_PARSERS = {
    "amet":    parse_amet_csv,
    "anu":     parse_anu_csv,
    "cdu":     parse_cdu_csv,
    "s-vyasa": parse_svyasa_csv,
}


def parse_csv(university_id: str, csv_path: str):
    parser = CSV_PARSERS.get(university_id)
    if not parser:
        raise ValueError(f"Unknown university_id '{university_id}'. Choose from: {list(CSV_PARSERS)}")
    return parser(csv_path)

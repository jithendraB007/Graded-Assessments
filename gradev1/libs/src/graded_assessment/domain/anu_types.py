from __future__ import annotations
from pydantic import BaseModel


class AnuSubQuestion(BaseModel):
    sub: str
    text: str
    co: str
    bloom: str


class AnuPartBQuestion(BaseModel):
    number: str
    text: str
    marks: str
    co: str
    bloom: str


class AnuPartA(BaseModel):
    sub_questions: list[AnuSubQuestion]


class AnuPartB(BaseModel):
    questions: list[AnuPartBQuestion]


class AnuAssessmentRequest(BaseModel):
    university_id: str = "anu"
    university_name: str
    batch: str
    exam_type: str
    course_name: str
    date: str
    duration: str
    max_marks: int
    notes: list[str]
    part_a: AnuPartA
    part_b: AnuPartB

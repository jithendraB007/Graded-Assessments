from __future__ import annotations
from pydantic import BaseModel


class SvyasaQuestion(BaseModel):
    number: str
    text: str
    co: str
    rbtl: str
    marks: int


class SvyasaQuestionPair(BaseModel):
    a: SvyasaQuestion
    b: SvyasaQuestion


class SvyasaPartA(BaseModel):
    questions: list[SvyasaQuestion]


class SvyasaPartB(BaseModel):
    question_pairs: list[SvyasaQuestionPair]


class SvyasaAssessmentRequest(BaseModel):
    university_id: str = "s-vyasa"
    month_year: str
    academic_year: str
    program: str
    specialization: str
    semester: str
    date_of_exam: str
    course_code: str
    course_name: str
    part_a: SvyasaPartA
    part_b: SvyasaPartB

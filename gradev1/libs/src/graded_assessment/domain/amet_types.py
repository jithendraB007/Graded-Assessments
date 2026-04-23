from __future__ import annotations
from pydantic import BaseModel


class AmetQuestion(BaseModel):
    number: str
    text: str
    mark: int
    btl: str
    co: str


class AmetQuestionPair(BaseModel):
    a: AmetQuestion
    b: AmetQuestion


class AmetPartA(BaseModel):
    total: str
    instruction: str
    questions: list[AmetQuestion]


class AmetPartB(BaseModel):
    total: str
    instruction: str
    question_pairs: list[AmetQuestionPair]


class AmetPartC(BaseModel):
    total: str
    instruction: str
    question: AmetQuestion


class AmetAssessmentRequest(BaseModel):
    university_id: str = "amet"
    exam_type: str
    programme: str
    semester: str
    course_name: str
    course_code: str
    duration: str
    max_marks: int
    instructions: list[str]
    part_a: AmetPartA
    part_b: AmetPartB
    part_c: AmetPartC

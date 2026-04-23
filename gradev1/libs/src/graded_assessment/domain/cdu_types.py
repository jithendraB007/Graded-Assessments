from __future__ import annotations
from pydantic import BaseModel


class CduQuestion(BaseModel):
    number: str
    text: str


class CduQuestionPair(BaseModel):
    a: CduQuestion
    b: CduQuestion


class CduSectionA(BaseModel):
    instruction: str
    questions: list[CduQuestion]


class CduSectionB(BaseModel):
    instruction: str
    question_pairs: list[CduQuestionPair]


class CduSet(BaseModel):
    label: str
    section_a: CduSectionA
    section_b: CduSectionB


class CduAssessmentRequest(BaseModel):
    university_id: str = "cdu"
    university_name: str
    course_info: str
    time: str
    max_marks: int
    sets: list[CduSet]

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, model_validator


class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    FILL_IN_THE_BLANK = "fill_in_the_blank"


class MCQOptions(BaseModel):
    a: str
    b: str
    c: str
    d: str


class Question(BaseModel):
    number: int
    text: str
    type: QuestionType
    marks: int
    options: MCQOptions | None = None

    @model_validator(mode="after")
    def _mcq_requires_options(self) -> Question:
        if self.type == QuestionType.MCQ and self.options is None:
            raise ValueError("MCQ questions must include 'options'")
        return self


class Section(BaseModel):
    letter: str
    type_name: str
    total_marks: int
    questions: list[Question]


class CoverPage(BaseModel):
    university_name: str
    department: str
    course_name: str
    assessment_title: str
    semester: str
    date: str


class Instructions(BaseModel):
    duration: str
    total_marks: int
    passing_marks: int
    attempt_rules: list[str]
    general_notes: list[str]


class GradedAssessmentRequest(BaseModel):
    university_id: str
    cover: CoverPage
    instructions: Instructions
    sections: list[Section]


class GradedAssessmentResult(BaseModel):
    output_path: str
    university_id: str

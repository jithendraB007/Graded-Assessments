import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "libs" / "src"))

from graded_assessment.application.generation_service import GradedAssessmentService
from graded_assessment.domain.types import (
    CoverPage, GradedAssessmentRequest, Instructions,
    MCQOptions, Question, QuestionType, Section,
)

request = GradedAssessmentRequest(
    university_id="test-university",
    cover=CoverPage(
        university_name="University of XYZ",
        department="Dept of Computer Science",
        course_name="Data Science 101",
        assessment_title="Mid-Term Graded Assessment",
        semester="Jan 2026",
        date="15 April 2026",
    ),
    instructions=Instructions(
        duration="2 Hours",
        total_marks=60,
        passing_marks=24,
        attempt_rules=[
            "All questions in Section A are compulsory.",
            "Attempt any 2 from Section B.",
        ],
        general_notes=[
            "No calculators allowed.",
            "Write clearly in blue or black ink.",
        ],
    ),
    sections=[
        Section(
            letter="A",
            type_name="Multiple Choice Questions",
            total_marks=20,
            questions=[
                Question(
                    number=1, text="What is Python?", type=QuestionType.MCQ, marks=2,
                    options=MCQOptions(a="A snake", b="A programming language", c="A database", d="An OS"),
                ),
                Question(
                    number=2, text="The capital of France is ____________.", type=QuestionType.FILL_IN_THE_BLANK, marks=1,
                ),
            ],
        ),
        Section(
            letter="B",
            type_name="Short Answer Questions",
            total_marks=20,
            questions=[
                Question(number=3, text="Explain the concept of recursion.", type=QuestionType.SHORT_ANSWER, marks=5),
                Question(number=4, text="What is the difference between a list and a tuple?", type=QuestionType.SHORT_ANSWER, marks=5),
            ],
        ),
        Section(
            letter="C",
            type_name="Long Answer Questions",
            total_marks=20,
            questions=[
                Question(number=5, text="Describe the steps involved in building a machine learning model from scratch.", type=QuestionType.LONG_ANSWER, marks=10),
            ],
        ),
    ],
)

result = GradedAssessmentService().generate(request)
print(f"\nDocument generated successfully!")
print(f"  Output: {result.output_path}")
print(f"  Size:   {Path(result.output_path).stat().st_size:,} bytes")
print(f"\nOpen the file in Word to review it.")

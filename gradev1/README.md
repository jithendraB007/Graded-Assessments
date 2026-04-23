# Graded Assessments

A Python library that generates university-branded Graded Assessment Word documents (`.docx`) for multiple universities, each with their own format, table structure, and question layout.

---

## Supported Universities

| University | ID | Format |
|---|---|---|
| AMET (Academy of Maritime Education and Training) | `amet` | 3-part table — Q.No, Question, Mark, BTL, CO |
| Annamacharya University | `anu` | 2-part — Part A (sub-questions a–e), Part B (long answer with OR) |
| Chaitanya Deemed University | `cdu` | Multi-set (Set A / B / C) — Section A & B, no CO/BTL |
| S-VYASA University | `s-vyasa` | 5-column table — Q.No, Questions, CO, RBTL, Marks with USN header |

---

## Project Structure

```
Graded-Assessments/
├── assets/
│   └── templates/              # University .docx template files
│       ├── AMET.docx
│       ├── ANU.docx
│       ├── ANU 2.docx
│       ├── CDU.docx
│       ├── S-Vyasa.docx
│       └── reference-assessment-template.docx   # Starter template for new universities
├── libs/
│   └── src/graded_assessment/
│       ├── domain/             # Pydantic request/response types per university
│       │   ├── amet_types.py
│       │   ├── anu_types.py
│       │   ├── cdu_types.py
│       │   ├── svyasa_types.py
│       │   └── types.py        # Generic assessment types
│       ├── application/
│       │   ├── generation_service.py   # Entry point — dispatches to correct renderer
│       │   ├── template_renderer.py    # Generic Jinja2 docxtpl renderer
│       │   └── renderers/
│       │       ├── amet_renderer.py
│       │       ├── anu_renderer.py
│       │       ├── cdu_renderer.py
│       │       └── svyasa_renderer.py
│       └── infrastructure/
│           └── docx_exporter.py        # Saves output .docx to artifacts/
├── skills/                     # Deep Agents skill trigger definitions
│   ├── amet/SKILL.md
│   ├── anu/SKILL.md
│   ├── cdu/SKILL.md
│   └── s-vyasa/SKILL.md
├── scripts/
│   └── create_assessment_reference_template.py  # One-time script to generate reference template
├── demo.py                     # Quick local test — generates all 4 university documents
└── main.py                     # FastAPI app (POST /generate, GET /health)
```

---

## Setup

**Requirements:** Python 3.11+, `python-docx`, `docxtpl`, `pydantic`

```bash
pip install python-docx docxtpl pydantic fastapi uvicorn
```

---

## Usage

### Run the demo (generates all 4 university documents)

```bash
python demo.py
```

Output files appear in `artifacts/graded-assessments/`.

### Use the service directly in code

```python
import sys
sys.path.insert(0, "libs/src")

from graded_assessment.application.generation_service import GradedAssessmentService
from graded_assessment.domain.amet_types import (
    AmetAssessmentRequest, AmetPartA, AmetPartB, AmetPartC, AmetQuestion, AmetQuestionPair
)

request = AmetAssessmentRequest(
    exam_type="MODEL EXAMINATIONS – APRIL 2026",
    programme="B.Tech SE/CSE",
    semester="II",
    course_name="Communicative English Advanced",
    course_code="256EN1A22TD",
    duration="3 hours",
    max_marks=100,
    instructions=["Ensure you have the correct question paper."],
    part_a=AmetPartA(
        total="20×1 = 20 Marks",
        instruction="Answer all the questions",
        questions=[
            AmetQuestion(number="1", text="Choose the correct option.", mark=1, btl="K2", co="CO1"),
        ]
    ),
    part_b=AmetPartB(
        total="5×14 = 70 Marks",
        instruction="Answer all the questions",
        question_pairs=[
            AmetQuestionPair(
                a=AmetQuestion(number="21 (a)", text="Write a paragraph.", mark=14, btl="K6", co="CO1"),
                b=AmetQuestion(number="21 (b)", text="Write an essay.", mark=14, btl="K6", co="CO1"),
            )
        ]
    ),
    part_c=AmetPartC(
        total="1×10 = 10 Marks",
        instruction="Answer the Question",
        question=AmetQuestion(number="26", text="Read the case study.", mark=10, btl="K3-K5", co="CO5")
    )
)

result = GradedAssessmentService().generate(request)
print(result.output_path)  # path to generated .docx
```

---

## Adding a New University

1. Place the branded `.docx` template in `assets/templates/{university_id}-assessment.docx`
2. Create domain types in `libs/src/graded_assessment/domain/{university_id}_types.py`
3. Create a renderer in `libs/src/graded_assessment/application/renderers/{university_id}_renderer.py`
4. Register the renderer in `generation_service.py` under `_RENDERER_MAP`
5. Create a skill trigger at `skills/{university_id}/SKILL.md`

---

## Skills

Each university has a `SKILL.md` that defines when an AI agent should trigger document generation for that university's format. Skills are picked up by the Deep Agents runtime.

---

## BTL / Bloom's Taxonomy Reference

| Level | AMET (BTL) | ANU (Bloom's) | S-VYASA (RBTL) |
|---|---|---|---|
| 1 | K1 | L1 | 1 |
| 2 | K2 | L2 | 2 |
| 3 | K3 | L3 | 3 |
| 4 | K4 | L4 | 4 |
| 5 | K5 | L5 | 5 |
| 6 | K6 | L6 | 6 |

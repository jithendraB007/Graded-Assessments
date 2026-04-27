# Graded Assessments

A Python library that generates university-branded Graded Assessment Word documents (`.docx`) for multiple universities. Each university has its own format, table structure, question layout, and branding. The system takes structured question data as input and produces a ready-to-print `.docx` file that matches the university's official paper format.

---

## How It Works

```
User / Agent provides question data
           │
           ▼
  GradedAssessmentService          ← entry point (generation_service.py)
           │
           │  looks up university_id in _RENDERER_MAP
           ▼
  University Renderer              ← e.g. amet_renderer.py
           │
           ├── open_template()     ← loads assets/templates/AMET.docx
           │                          clears body, keeps page layout
           ├── insert_logo()       ← inserts assets/logos/amet.png
           │
           ├── builds header block
           ├── builds question tables (Part A, Part B, Part C)
           │
           ▼
  docx_exporter.py
           │
           ▼
  artifacts/graded-assessments/{university}-assessment-{id}.docx
```

### Step-by-step flow

1. You create a typed request object (e.g. `AmetAssessmentRequest`) and pass it to `GradedAssessmentService().generate(request)`.
2. The service looks up the `university_id` field in its renderer map and calls the matching renderer.
3. The renderer opens the university's `.docx` template from `assets/templates/`, clears all body content while keeping the page margins and fonts, then inserts the logo from `assets/logos/` if one exists.
4. The renderer builds the document — header metadata, instruction text, question tables — using `python-docx` with raw XML borders so the output works regardless of which styles the template has.
5. The finished document bytes are passed to the exporter, which saves them to `artifacts/graded-assessments/` with a unique filename and returns the path.

---

## Project Structure

```
gradev1/
├── assets/
│   ├── templates/                  ← One .docx per university (page layout source)
│   │   ├── AMET.docx
│   │   ├── ANU.docx
│   │   ├── CDU.docx
│   │   └── S-Vyasa.docx
│   └── logos/                      ← University logos (PNG or JPG)
│       ├── amet.png                ← Extracted from AMET.docx
│       └── s-vyasa.jpg             ← Extracted from S-Vyasa.docx
│
├── libs/src/graded_assessment/
│   ├── domain/                     ← Pydantic types — one file per university
│   │   ├── amet_types.py
│   │   ├── anu_types.py
│   │   ├── cdu_types.py
│   │   ├── svyasa_types.py
│   │   └── types.py                ← Generic fallback types
│   ├── application/
│   │   ├── generation_service.py   ← Dispatches to the right renderer
│   │   ├── template_renderer.py    ← Generic Jinja2 / docxtpl fallback
│   │   └── renderers/
│   │       ├── _base.py            ← Shared: open_template, insert_logo, set_table_borders
│   │       ├── amet_renderer.py
│   │       ├── anu_renderer.py
│   │       ├── cdu_renderer.py
│   │       └── svyasa_renderer.py
│   └── infrastructure/
│       └── docx_exporter.py        ← Saves bytes to artifacts/, returns file path
│
├── skills/                         ← Self-contained skill folders (upload to Claude web)
│   ├── amet/
│   │   ├── SKILL.md                ← Tells AI agents when and how to use this skill
│   │   ├── generate.py             ← Standalone script, no external lib imports
│   │   └── assets/                 ← Local copy of template + logo
│   ├── anu/
│   ├── cdu/
│   └── s-vyasa/
│
├── artifacts/graded-assessments/   ← All generated .docx files are saved here
├── demo.py                         ← Generates all 4 university documents with sample data
├── main.py                         ← FastAPI server (POST /generate, GET /health)
└── libs/pyproject.toml             ← Package metadata and dependencies
```

---

## Supported Universities

| University | ID | Document Format |
|---|---|---|
| AMET (Academy of Maritime Education and Training) | `amet` | 5-column table — Question No, Question, Mark, BTL, CO — three parts: A (20 MCQ), B (5 OR pairs × 14M), C (case study 10M) |
| Annamacharya University | `anu` | Hall Ticket row + 6-column tables — Part A has 5 sub-questions (a–e) under Q1, Part B has long-answer questions with OR rows |
| Chaitanya Deemed University | `cdu` | Three identical sets (Set A / B / C) each with Section A (10 short Q, answer any 6) and Section B (question pairs with OR) |
| S-VYASA University | `s-vyasa` | USN row + 4-column header metadata + 5-column tables — Part A (10 Q × 3M = 30), Part B (5 pairs × 14M = 70) |

---

## Setup

### Prerequisites

- Python 3.11 or higher
- Microsoft Word or LibreOffice (to open generated files)

### Install Dependencies

```bash
pip install python-docx docxtpl pydantic
```

For the FastAPI server (`main.py`) also install:

```bash
pip install fastapi uvicorn
```

### Verify the Templates Are Present

The four university template files must exist in `assets/templates/`:

```
assets/templates/AMET.docx
assets/templates/ANU.docx
assets/templates/CDU.docx
assets/templates/S-Vyasa.docx
```

Logos are optional. If present, they are placed at the top of the document:

```
assets/logos/amet.png
assets/logos/s-vyasa.jpg
```

---

## Running the Application

### Option 1 — Demo Script (recommended first test)

Generates all 4 university documents with realistic sample questions:

```bash
python demo.py
```

Output:

```
============================================================
  GENERATED DOCUMENTS
============================================================
  AMET         amet-assessment-a1b2c3d4.docx  (544,645 bytes)
  ANU          anu-assessment-e5f6g7h8.docx   (8,552 bytes)
  CDU          cdu-assessment-i9j0k1l2.docx   (9,284 bytes)
  S-Vyasa      s-vyasa-assessment-m3n4.docx   (20,535 bytes)
============================================================

All files saved in: d:\gradev1\artifacts\graded-assessments\
```

Open each file in Microsoft Word to review.

### Option 2 — Use the Library in Your Own Code

```python
import sys
sys.path.insert(0, "libs/src")

from graded_assessment.application.generation_service import GradedAssessmentService
from graded_assessment.domain.amet_types import (
    AmetAssessmentRequest, AmetPartA, AmetPartB, AmetPartC,
    AmetQuestion, AmetQuestionPair,
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
            # ... 19 more questions
        ],
    ),
    part_b=AmetPartB(
        total="5×14 = 70 Marks",
        instruction="Answer all the questions",
        question_pairs=[
            AmetQuestionPair(
                a=AmetQuestion(number="21 (a)", text="Write a paragraph.", mark=14, btl="K6", co="CO1"),
                b=AmetQuestion(number="21 (b)", text="Write an essay.", mark=14, btl="K6", co="CO1"),
            ),
            # ... 4 more pairs
        ],
    ),
    part_c=AmetPartC(
        total="1×10 = 10 Marks",
        instruction="Answer the Question",
        question=AmetQuestion(number="26", text="Read the case study.", mark=10, btl="K3-K5", co="CO5"),
    ),
)

result = GradedAssessmentService().generate(request)
print(result.output_path)   # path to the generated .docx file
```

### Option 3 — FastAPI Server

Start the server:

```bash
python main.py
```

Send a POST request to generate a document:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{ "university_id": "amet", ... }' \
  --output assessment.docx
```

Check server health:

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

> **Windows note:** If `uvicorn` fails to start due to an SSL DLL error caused by App Control policy, use `demo.py` or the standalone skill scripts instead.

---

## Standalone Skills (Upload to Claude Web)

Each university skill folder is fully self-contained — it has its own `generate.py`, template, and logo. No shared library imports are needed.

```
skills/amet/
├── SKILL.md          ← Tells AI when to trigger this skill
├── generate.py       ← All types + rendering logic in one file
└── assets/
    ├── templates/AMET.docx
    └── logos/amet.png
```

To use standalone:

```bash
cd skills/amet
python -c "
from generate import generate, AmetAssessmentRequest, ...
result = generate(request)
print(result)
"
```

Output is saved to `skills/amet/artifacts/`.

To upload to Claude web: upload `SKILL.md`, `generate.py`, and the `assets/` folder from any skill directory.

---

## Google Drive Integration

The project integrates with Google Drive, Docs, and Sheets through the `gws` CLI.

### Installed Skills

| Skill | What it does |
|---|---|
| `gws-shared` | Auth, global flags, security rules |
| `gws-docs` | Read and write Google Docs |
| `gws-docs-write` | Append plain text to a Doc |
| `gws-sheets-read` | Read a range from a Sheet |

### Common Commands

Upload a generated assessment to Drive:

```powershell
gws drive +upload --file "d:\gradev1\artifacts\graded-assessments\amet-assessment.docx"
```

Read question data from a Google Sheet:

```powershell
gws sheets +read --spreadsheet SPREADSHEET_ID --range "Sheet1!A1:F50"
```

Append content to a Google Doc:

```powershell
gws docs +write --document DOCUMENT_ID --text "Content to append"
```

Re-authenticate:

```powershell
C:\tools\gws.exe auth login
```

---

## Adding a New University

1. Place the university's branded `.docx` in `assets/templates/{UniName}.docx`
2. Add a logo to `assets/logos/{university_id}.png` (optional)
3. Create domain types in `libs/src/graded_assessment/domain/{university_id}_types.py`
4. Create a renderer in `libs/src/graded_assessment/application/renderers/{university_id}_renderer.py`
   - Start with `doc = open_template("{UniName}")` and `insert_logo(doc, "{university_id}")`
   - Use `set_table_borders(table)` for all tables
5. Register the renderer in `generation_service.py`:
   ```python
   _RENDERER_MAP = {
       ...
       "{university_id}": {university_id}_renderer.render,
   }
   ```
6. Create a self-contained skill at `skills/{university_id}/` with `SKILL.md` and `generate.py`

---

## Bloom's Taxonomy / BTL Reference

| Level | Meaning | AMET | ANU | S-VYASA |
|---|---|---|---|---|
| 1 | Remember | K1 | L1 | 1 |
| 2 | Understand | K2 | L2 | 2 |
| 3 | Apply | K3 | L3 | 3 |
| 4 | Analyse | K4 | L4 | 4 |
| 5 | Evaluate | K5 | L5 | 5 |
| 6 | Create | K6 | L6 | 6 |

CDU does not use BTL or CO columns.

# Graded Assessments

A Python library that generates university-branded Graded Assessment Word documents (`.docx`).
It reads question data from **Google Sheets**, generates the document using a university-specific
template, and uploads the result to **Google Drive** — all in one command.

---

## How It Works

```
Google Sheets  -->  pipeline.py  -->  .docx renderer  -->  Google Drive
(question data)     (orchestrator)    (per university)     (upload)
```

Step by step:

1. You fill a Google Sheet with exam metadata and questions (one tab per section).
2. Run `pipeline.py` — it reads the sheet via the `gws` CLI, builds a typed request object, passes it to `GradedAssessmentService`, which calls the right university renderer.
3. The renderer opens the university `.docx` template, clears its body, inserts the logo, builds the header and question tables, and saves the file to `artifacts/graded-assessments/`.
4. The pipeline uploads the file to Google Drive and prints a direct link.

---

## Supported Universities

| University | ID | Format |
|---|---|---|
| AMET (Academy of Maritime Education and Training) | `amet` | Part A — 20 MCQ (1M each) · Part B — 5 OR pairs (14M each) · Part C — case study (10M) |
| Annamacharya University | `anu` | Part A — 5 sub-questions (a–e) under Q1 · Part B — long answer with OR rows |
| Chaitanya Deemed University | `cdu` | Set A / B / C — each with Section A (10 short Q) and Section B (question pairs with OR) |
| S-VYASA University | `s-vyasa` | USN row · header metadata · Part A (10 Q × 3M = 30) · Part B (5 pairs × 14M = 70) |

---

## Project Structure

```
gradev1/
├── .agents/skills/
│   ├── generate/
│   │   └── generate.py         <- shared generator used by all university skills
│   ├── amet/
│   │   ├── SKILL.md            <- tells AI agents when to trigger AMET generation
│   │   └── assets/
│   │       ├── templates/AMET.docx
│   │       └── logos/amet.png
│   ├── anu/
│   │   ├── SKILL.md
│   │   └── assets/templates/ANU.docx
│   ├── cdu/
│   │   ├── SKILL.md
│   │   └── assets/templates/CDU.docx
│   ├── s-vyasa/
│   │   ├── SKILL.md
│   │   └── assets/
│   │       ├── templates/S-Vyasa.docx
│   │       └── logos/s-vyasa.jpg
│   ├── gws-shared/SKILL.md     <- gws auth + global flags reference
│   ├── gws-docs/SKILL.md       <- read/write Google Docs
│   ├── gws-docs-write/SKILL.md <- append text to a Google Doc
│   └── gws-sheets-read/SKILL.md<- read values from Google Sheets
│
├── assets/
│   ├── templates/              <- master university .docx templates
│   │   ├── AMET.docx
│   │   ├── ANU.docx
│   │   ├── CDU.docx
│   │   └── S-Vyasa.docx
│   └── logos/                  <- university logos (extracted from templates)
│       ├── amet.png
│       └── s-vyasa.jpg
│
├── integrations/
│   ├── gws_client.py           <- subprocess wrapper: read_sheet(), upload_to_drive()
│   └── sheet_parsers.py        <- parses sheet tabs into typed request objects
│
├── libs/src/graded_assessment/
│   ├── domain/                 <- Pydantic types per university
│   │   ├── amet_types.py
│   │   ├── anu_types.py
│   │   ├── cdu_types.py
│   │   └── svyasa_types.py
│   ├── application/
│   │   ├── generation_service.py   <- dispatches to right renderer by university_id
│   │   └── renderers/
│   │       ├── _base.py            <- open_template(), insert_logo(), set_table_borders()
│   │       ├── amet_renderer.py
│   │       ├── anu_renderer.py
│   │       ├── cdu_renderer.py
│   │       └── svyasa_renderer.py
│   └── infrastructure/
│       └── docx_exporter.py        <- saves .docx bytes to artifacts/
│
├── scripts/
│   └── create_test_sheet.py    <- creates a Google Sheet with AMET sample data for testing
│
├── artifacts/graded-assessments/   <- all generated .docx files saved here
├── pipeline.py                 <- main entry point: Sheets -> generate -> Drive
├── demo.py                     <- local test: generates all 4 universities offline
└── main.py                     <- FastAPI server (POST /generate, GET /health)
```

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | python.org |
| pip | any | bundled with Python |
| gws CLI | 0.22.5+ | See Google Workspace CLI Setup below |
| Microsoft Word or LibreOffice | any | To open generated files |

---

## Part 1 — Python Setup

### 1. Clone the repository

```bash
git clone https://github.com/jithendraB007/Graded-Assessments.git
cd Graded-Assessments/gradev1
```

### 2. Install Python dependencies

```bash
pip install python-docx docxtpl pydantic
```

For the FastAPI server also install:

```bash
pip install fastapi uvicorn
```

---

## Part 2 — Google Workspace CLI Setup

The `gws` CLI handles all Google Drive and Sheets interactions.

### 1. Download and install gws

1. Go to: `https://github.com/googleworkspace/cli/releases/latest`
2. Download `google-workspace-cli-x86_64-pc-windows-msvc.zip`
3. Extract and copy `gws.exe` to `C:\tools\`
4. Add `C:\tools` to your system PATH (run once in PowerShell as Administrator):

```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\tools", "Machine")
```

5. Restart your terminal and verify:

```powershell
gws --version
# gws 0.22.5
```

### 2. Create Google Cloud credentials

1. Open `https://console.cloud.google.com`
2. Create or select a project
3. Enable these APIs in **APIs & Services → Library**:
   - Google Drive API
   - Google Docs API
   - Google Sheets API
4. Go to **APIs & Services → OAuth consent screen**:
   - User type: **External**
   - Add your Gmail as a **Test user**
5. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**
   - Download the JSON file
6. Rename it to `client_secret.json` and save it here:

```
C:\Users\<YourName>\.config\gws\client_secret.json
```

> **Common mistake:** Windows sometimes saves it as `client_secret.json.json` (double extension).
> Check with: `dir C:\Users\<YourName>\.config\gws\`

### 3. Authenticate

```powershell
C:\tools\gws.exe auth login
```

A browser window opens. Sign in, click **Continue** past the unverified app warning, then **Allow**.

Verify it works:

```powershell
C:\tools\gws.exe drive files list
# {"files": [...], "kind": "drive#fileList"}
```

### 4. Install the agent skills

```powershell
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-shared --yes
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-docs --yes
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-docs-write --yes
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-sheets-read --yes
```

---

## Part 3 — Running the Application

### Option A — Full pipeline (Google Sheets → generate → Google Drive)

#### Step 1: Create your Google Sheet

Each university uses a specific tab structure. See the **Google Sheet Structure** section below for the exact layout.

To create a test sheet with AMET sample data automatically:

```bash
python scripts/create_test_sheet.py
```

This creates a ready-to-use Google Sheet and prints its ID and URL.

#### Step 2: Run the pipeline

```bash
python pipeline.py --university amet     --spreadsheet SHEET_ID
python pipeline.py --university anu      --spreadsheet SHEET_ID
python pipeline.py --university cdu      --spreadsheet SHEET_ID
python pipeline.py --university s-vyasa  --spreadsheet SHEET_ID
```

Upload directly into a Drive folder:

```bash
python pipeline.py --university amet --spreadsheet SHEET_ID --folder DRIVE_FOLDER_ID
```

Parse and preview without generating:

```bash
python pipeline.py --university amet --spreadsheet SHEET_ID --dry-run
```

Output:

```
[1/3] Reading AMET questions from Google Sheets...
      Done — request parsed successfully.

[2/3] Generating .docx document...
      Saved -> D:\gradev1\artifacts\graded-assessments\amet-assessment-56467994.docx

[3/3] Uploading to Google Drive...
      Uploaded -> amet-assessment-56467994.docx
      Drive ID -> 1MvwCvVzSXF...
      Link     -> https://drive.google.com/file/d/1MvwCvVzSXF.../view

Done.
```

### Option B — Shared agent generator (used by AI agent skills)

```bash
python .agents/skills/generate/generate.py --university amet --spreadsheet SHEET_ID
python .agents/skills/generate/generate.py --university anu  --spreadsheet SHEET_ID --folder FOLDER_ID
```

### Option C — Local demo (no Google Sheets, no internet)

Generates all 4 university documents with built-in sample questions:

```bash
python demo.py
```

Output files appear in `artifacts/graded-assessments/`. Open in Word to review.

### Option D — FastAPI server

```bash
python main.py
```

```bash
curl http://localhost:8000/health
# {"status": "ok"}

curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"university_id": "amet", ...}' \
  --output assessment.docx
```

> **Windows note:** If uvicorn fails to start due to an SSL DLL policy error, use `demo.py` or `pipeline.py` instead.

---

## Google Sheet Structure

### AMET (5 tabs)

**Config** tab — key / value pairs:

| key | value |
|---|---|
| exam_type | MODEL EXAMINATIONS – APRIL 2026 |
| programme | B.Tech SE/CSE |
| semester | II |
| course_name | Communicative English Advanced |
| course_code | 256EN1A22TD |
| duration | 3 hours |
| max_marks | 100 |
| part_a_total | 20×1 = 20 Marks |
| part_a_instruction | Answer all the questions |
| part_b_total | 5×14 = 70 Marks |
| part_b_instruction | Answer all the questions |
| part_c_total | 1×10 = 10 Marks |
| part_c_instruction | Answer the Question |

**Instructions** tab — one row per instruction:

| instruction |
|---|
| Before attempting any question paper... |

**Part_A** tab — one row per question:

| number | text | mark | btl | co |
|---|---|---|---|---|
| 1 | Choose the correct option... | 1 | K2 | CO1 |

**Part_B** tab — one row per option (a and b), grouped by pair number:

| pair | option | number | text | mark | btl | co |
|---|---|---|---|---|---|---|
| 1 | a | 21 (a) | Write a paragraph... | 14 | K6 | CO1 |
| 1 | b | 21 (b) | Write an essay... | 14 | K6 | CO1 |

**Part_C** tab — single question row:

| number | text | mark | btl | co |
|---|---|---|---|---|
| 26 | Read the case study... | 10 | K3-K5 | CO5 |

---

### ANU (4 tabs)

**Config**: university_name, batch, exam_type, course_name, date, duration, max_marks

**Notes**: `note` column — one row per exam rule

**Part_A**: `sub | text | co | bloom`

**Part_B**: `number | text | marks | co | bloom`
Use `(OR)` in the `number` column for OR separator rows.

---

### CDU (4 tabs)

**Config**: university_name, course_info, time, max_marks, section_a_instruction, section_b_instruction

**Set_A / Set_B / Set_C**: `section | pair | number | text`
- `section` = `A` for Section A questions, `B` for Section B questions
- `pair` = `1`, `2`, ... (used to group Section B question pairs)

---

### S-VYASA (3 tabs)

**Config**: month_year, academic_year, program, specialization, semester, date_of_exam, course_code, course_name

**Part_A**: `number | text | co | rbtl | marks`

**Part_B**: `pair | option | number | text | co | rbtl | marks`

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

---

## Adding a New University

1. Add the branded `.docx` template to `assets/templates/{UniName}.docx`
2. Add a logo to `assets/logos/{university_id}.png` (optional)
3. Create domain types in `libs/src/graded_assessment/domain/{university_id}_types.py`
4. Create a renderer in `libs/src/graded_assessment/application/renderers/{university_id}_renderer.py`
   - Start with `open_template()`, `insert_logo()`, and `set_table_borders()` from `_base.py`
5. Register the renderer in `generation_service.py` inside `_RENDERER_MAP`
6. Add a parser to `integrations/sheet_parsers.py` and register it in `PARSERS`
7. Create `.agents/skills/{university_id}/SKILL.md` with the trigger description

---

## Key Commands Reference

```bash
# Test sheet creation (AMET sample data)
python scripts/create_test_sheet.py

# Run pipeline for any university
python pipeline.py --university <id> --spreadsheet <SHEET_ID> [--folder <DRIVE_FOLDER_ID>]

# Run shared agent generator
python .agents/skills/generate/generate.py --university <id> --spreadsheet <SHEET_ID>

# Local offline test (all 4 universities)
python demo.py

# Upload a file to Drive manually
C:\tools\gws.exe drive +upload "path\to\file.docx" --parent FOLDER_ID

# Re-authenticate gws
C:\tools\gws.exe auth login
```

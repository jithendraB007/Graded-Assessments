# Graded Assessments

A Python library that generates university-branded Graded Assessment Word documents (`.docx`).
It reads question data from **Google Sheets**, generates the document using a university-specific
template, and uploads the result to the university's **Google Drive folder** — all in one command.

---

## How It Works

```
Google Sheets  -->  generate.py  -->  .docx renderer  -->  Google Drive (university folder)
(question data)     (orchestrator)    (per university)     (date-stamped file)
```

Step by step:

1. You fill a Google Sheet with exam metadata and questions (one tab per section).
2. Run `generate.py` — it reads the sheet via the `gws` CLI, builds a typed request object,
   passes it to `GradedAssessmentService`, which calls the right university renderer.
3. The renderer opens the university `.docx` template, clears its body, inserts the logo,
   builds the header and question tables, and saves the file to `artifacts/graded-assessments/`.
4. The file is uploaded to that university's dedicated Google Drive folder and a direct link is printed.

---

## Quick Start

### Run the generator (Sheets -> generate .docx -> upload to Drive)

```bash
python .agents/skills/generate/generate.py --university amet     --spreadsheet SHEET_ID
python .agents/skills/generate/generate.py --university anu      --spreadsheet SHEET_ID
python .agents/skills/generate/generate.py --university cdu      --spreadsheet SHEET_ID
python .agents/skills/generate/generate.py --university s-vyasa  --spreadsheet SHEET_ID

# Override Drive folder (optional — defaults to university's own folder)
python .agents/skills/generate/generate.py --university amet --spreadsheet SHEET_ID --folder DRIVE_FOLDER_ID

# Dry run — parse and preview without generating
python .agents/skills/generate/generate.py --university amet --spreadsheet SHEET_ID --dry-run
```

---

### gws utility commands

```bash
# Re-authenticate with Google
C:\tools\gws.exe auth login

# List all files in your Drive
C:\tools\gws.exe drive files list

# Read a specific tab from a Google Sheet
C:\tools\gws.exe sheets +read --spreadsheet SHEET_ID --range "Config!A1:B15"

# Upload a .docx manually to Drive
C:\tools\gws.exe drive +upload "D:\gradev1\artifacts\graded-assessments\amet-assessment-2026-04-28.docx"

# Upload into a specific Drive folder
C:\tools\gws.exe drive +upload "path\to\file.docx" --parent DRIVE_FOLDER_ID
```

---

## Supported Universities

| University | ID | Drive Folder |
|---|---|---|
| AMET (Academy of Maritime Education and Training) | `amet` | AMET University |
| Annamacharya University | `anu` | ANU University |
| Chaitanya Deemed University | `cdu` | CUD University |
| S-VYASA University | `s-vyasa` | s-vyasa University |

Each university's files are uploaded automatically to its dedicated Drive folder, named
`{university}-assessment-{date}.docx` (e.g. `amet-assessment-2026-04-28.docx`).

---

## Project Structure

```
gradev1/
├── .agents/skills/
│   ├── generate/
│   │   └── generate.py         <- entry point: Sheets -> generate -> Drive
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
│   └── logos/                  <- university logos
│       ├── amet.png
│       └── s-vyasa.jpg
│
├── integrations/
│   ├── drive_folders.py        <- maps university_id -> Drive folder ID
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
│   │       ├── _base.py            <- shared helpers: open_template, insert_logo, set_table_borders, set_col_widths, set_document_font
│   │       ├── amet_renderer.py
│   │       ├── anu_renderer.py
│   │       ├── cdu_renderer.py
│   │       └── svyasa_renderer.py
│   └── infrastructure/
│       └── docx_exporter.py        <- saves .docx to artifacts/ with date-stamped filename
│
└── artifacts/graded-assessments/   <- all generated .docx files saved here
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

---

## Part 3 — Running the Generator

```bash
python .agents/skills/generate/generate.py --university amet     --spreadsheet SHEET_ID
python .agents/skills/generate/generate.py --university anu      --spreadsheet SHEET_ID
python .agents/skills/generate/generate.py --university cdu      --spreadsheet SHEET_ID
python .agents/skills/generate/generate.py --university s-vyasa  --spreadsheet SHEET_ID
```

Output:

```
[1/3] Reading AMET questions from Google Sheets...
      Parsed successfully.

[2/3] Generating .docx document...
      Saved -> D:\gradev1\artifacts\graded-assessments\amet-assessment-2026-04-28.docx

[3/3] Uploading to Google Drive...
      Folder -> AMET university folder
      File   -> amet-assessment-2026-04-28.docx
      Link   -> https://drive.google.com/file/d/1.../view

Done.
```

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
5. Register the renderer in `generation_service.py` inside `_RENDERER_MAP`
6. Add a parser to `integrations/sheet_parsers.py` and register it in `PARSERS`
7. Add the Drive folder ID to `integrations/drive_folders.py`
8. Create `.agents/skills/{university_id}/SKILL.md` with the trigger description

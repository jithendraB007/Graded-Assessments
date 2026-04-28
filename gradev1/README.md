# Graded Assessment Generator

You give questions — as a CSV file or by pasting them in chat — and the system
automatically generates a university-branded Word document and saves it to that
university's Google Drive folder with today's date.

---

## Supported Universities

| University | Skill folder | Drive folder |
|---|---|---|
| AMET (Academy of Maritime Education and Training) | `.agents/skills/amet/` | AMET University |
| Annamacharya University (ANU) | `.agents/skills/anu/` | ANU University |
| Chaitanya Deemed University (CDU) | `.agents/skills/cdu/` | CDU University |
| S-VYASA University | `.agents/skills/s-vyasa/` | S-VYASA University |

Each skill folder contains:
- `SKILL.md` — tells the AI what format the university uses and when to trigger it
- `assets/sample_questions.csv` — a ready-to-use CSV you can fill in and run

---

## How to Give Questions

There are two ways.

### Way 1 — Upload a CSV file

1. Copy the sample CSV for your university from  
   `.agents/skills/<university>/assets/sample_questions.csv`
2. Fill in your questions (keep the column format exactly as shown)
3. Run:

```bash
python .agents/skills/generate/generate.py --university amet     --csv your_file.csv
python .agents/skills/generate/generate.py --university anu      --csv your_file.csv
python .agents/skills/generate/generate.py --university cdu      --csv your_file.csv
python .agents/skills/generate/generate.py --university s-vyasa  --csv your_file.csv
```

The document is saved to `artifacts/graded-assessments/` and uploaded to the
university's Drive folder automatically.

---

### Way 2 — Paste questions in Claude / Codex chat

Open Claude Code or Codex and paste your questions directly in the chat along
with the exam details (university name, course name, duration, marks, etc.).
The AI reads the SKILL.md for that university, formats everything correctly, and
runs the generator for you. No CSV needed.

---

## CSV Format (Quick Reference)

Every CSV has 8 columns: `section, f1, f2, f3, f4, f5, f6, f7`

Lines starting with `#` are comments and are ignored.

| University | Config keys (f1) | Question sections |
|---|---|---|
| AMET | exam_type, programme, semester, course_name, course_code, duration, max_marks | `part_a`, `part_b`, `part_c` |
| ANU | university_name, batch, exam_type, course_name, date, duration, max_marks | `part_a`, `part_b` (use `(OR)` in f1 for OR rows) |
| CDU | university_name, course_info, time, max_marks, section_a_instruction, section_b_instruction | `set_a_a`, `set_a_b`, `set_b_a`, `set_b_b`, `set_c_a`, `set_c_b` |
| S-VYASA | month_year, academic_year, program, specialization, semester, date_of_exam, course_code, course_name | `part_a`, `part_b` |

Open the sample CSV for your university to see a complete filled-in example.

---

## Where the Output Goes

Generated files are saved in two places:

1. **Locally** — `artifacts/graded-assessments/<university>-assessment-<date>.docx`
2. **Google Drive** — uploaded automatically to the university's dedicated folder

The terminal prints a direct Drive link when the upload is done.

---

## One-Time Setup

### Step 1 — Install Python dependencies

```bash
pip install python-docx pydantic
```

### Step 2 — Install the gws CLI

1. Download from: `https://github.com/googleworkspace/cli/releases/latest`
   — pick `google-workspace-cli-x86_64-pc-windows-msvc.zip`
2. Extract and place `gws.exe` in `C:\tools\`
3. Add `C:\tools` to your system PATH (run once in PowerShell as Administrator):

```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\tools", "Machine")
```

4. Restart your terminal and verify:

```powershell
gws --version
```

---

### Step 3 — Set up Google Cloud credentials

This is a one-time step. You need a Google Cloud project with OAuth credentials
so the tool can read/write your Google Drive.

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or select an existing one)
3. Go to **APIs & Services → Library** and enable:
   - Google Drive API
   - Google Sheets API
4. Go to **APIs & Services → OAuth consent screen**:
   - User type: **External**
   - Fill in the app name (anything, e.g. "Graded Assessment Tool")
   - Click **Save and Continue** through the remaining screens
5. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**
   - Click **Create** and download the JSON file
6. Rename the downloaded file to `client_secret.json`
7. Save it here:

```
C:\Users\<YourName>\.config\gws\client_secret.json
```

> Windows sometimes saves it as `client_secret.json.json` (double extension).
> Check with: `dir C:\Users\<YourName>\.config\gws\`

---

### Step 4 — Add a user's Gmail to the project

If someone else needs to run this tool with their Google account, you must add
their Gmail address as a **Test User** in the Google Cloud project.

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and open your project
2. Go to **APIs & Services → OAuth consent screen**
3. Scroll down to the **Test users** section
4. Click **+ Add Users**
5. Enter the person's Gmail address and click **Save**

That person can now authenticate with their own account by running:

```bash
gws auth login
```

> Until the app is published, only Gmail addresses listed as Test Users can log in.
> You can add up to 100 test users.

---

### Step 5 — Authenticate

```bash
gws auth login
```

A browser window opens. Sign in with your Gmail, click **Continue** past the
"unverified app" warning, then **Allow**.

Verify it works:

```bash
gws drive files list
```

If you see a JSON list of Drive files, you're authenticated.

---

## Important Notes

- **Drive folders** — The four university Drive folders already exist and are
  pre-configured. Files go into the correct folder automatically based on the
  `--university` argument. You do not need to set up anything in Drive.

- **Logos** — University logos are embedded in the `.docx` templates. If a logo
  is missing or needs updating, replace the file in `assets/logos/` (AMET uses
  `amet.png`, S-VYASA uses `s-vyasa.jpg`).

- **Date in filename** — The output file always uses today's date, e.g.
  `amet-assessment-2026-04-28.docx`. Running it twice on the same day will
  overwrite the file in `artifacts/` but upload a new copy to Drive.

- **CDU has three sets** — CDU generates one document containing Set A, Set B,
  and Set C (each on a new page). The CSV uses `set_a_*`, `set_b_*`, `set_c_*`
  section prefixes to distinguish them.

- **ANU OR rows** — In the ANU Part B CSV, put `(OR)` in the `f1` column to
  insert an OR separator between question pairs.

- **Re-authenticating** — If you get an authentication error after a while, run
  `gws auth login` again to refresh the token.

---

## Adding a New University

1. Add the branded `.docx` template to `assets/templates/{UniName}.docx`
2. Add a logo to `assets/logos/{university_id}.png` (optional)
3. Create domain types in `libs/src/graded_assessment/domain/{university_id}_types.py`
4. Create a renderer in `libs/src/graded_assessment/application/renderers/{university_id}_renderer.py`
5. Register the renderer in `libs/src/graded_assessment/application/generation_service.py`
6. Add a CSV parser to `integrations/csv_parsers.py`
7. Add the Drive folder ID to `integrations/drive_folders.py`
8. Create a skill folder `.agents/skills/{university_id}/` with `SKILL.md` and a sample CSV

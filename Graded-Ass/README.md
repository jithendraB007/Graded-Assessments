# Question Paper Generator

An automated Streamlit web application that fills a Word document template with questions from your dataset and then runs an AI-powered quality judge on every inserted question — no manual copy-paste or manual review needed.

---

## How It Works

```
You upload two files
        │
        ├── Word Template (.docx)  ←  Contains {{PLACEHOLDER}} markers
        └── Question Dataset (.csv / .xlsx)  ←  Your question bank
                │
                ▼
        App reads the template and finds all {{...}} markers
                │
                ▼
        App filters questions from the dataset
        (by topic, subtopic, difficulty, question type)
                │
                ▼
        Questions are inserted into the correct sections
        (original formatting preserved, no duplicates)
                │
                ▼
        AI Quality Judge reviews every inserted question
        (Grammar · Clarity · Difficulty alignment · Format)
                │
                ▼
        Per-question verdict: Pass / Revise / Fail
        User confirms or overrides verdicts → builds training data
                │
                ▼
        Download the ready-to-use question paper (.docx)
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your Mistral API key

Copy `.env.example` to `.env` and fill in your key:
```bash
cp .env.example .env
```
Then edit `.env`:
```
MISTRAL_API_KEY=your-key-here
MISTRAL_MODEL=mistral-small-latest
```
Get a free key at [console.mistral.ai](https://console.mistral.ai/). The API key is only needed for the quality judge — the paper generator works without it.

### 3. (Optional) Generate the sample template
```bash
python create_sample_template.py
```
This creates `sample_data/template.docx` which you can use to test the app immediately.

### 4. Run the app
```bash
streamlit run app.py
```
Opens in your browser at `http://localhost:8501`.

---

## App Walkthrough — Step by Step

### Step 1: Upload Files

| Upload slot | What to provide |
|---|---|
| **Word Template (.docx)** | Your exam paper skeleton containing `{{PLACEHOLDER}}` markers |
| **Question Dataset (.csv or .xlsx)** | Your question bank spreadsheet |

A live preview of the first 10 rows of your dataset appears automatically after upload.

---

### Step 2: Configure Paper

| Field | Description |
|---|---|
| **Topic** | Must match the `topic` column in your dataset exactly (case-insensitive). E.g. `English Grammar` |
| **Subtopic** | Must match the `subtopic` column exactly. E.g. `Tenses` |
| **Easy Questions** | How many Easy questions per Easy placeholder (default: 5) |
| **Medium Questions** | How many Medium questions per Medium placeholder (default: 3) |
| **Hard Questions** | How many Hard questions per Hard placeholder (default: 2) |
| **Question Pattern / Exam Format** | Optional note for your own reference |

> If a placeholder encodes a count in its name (e.g. `{{EASY_MCQ_5}}`), that number overrides the form value for that specific section.

---

### Step 3: Generate

- Click **Generate Question Paper**.
- The app inserts questions into every recognised placeholder while preserving all existing formatting.
- Any shortfall warnings (not enough questions in the dataset) appear in an expandable panel.
- The **Download question_paper.docx** button appears immediately after generation.

---

### Step 4: Quality Judge

The AI judge evaluates every inserted question for English language quality using **DSPy + Mistral AI**. It automatically loads an optimized prompt from `artifacts/` if one exists, otherwise runs zero-shot.

#### How to run it

1. Make sure your Mistral API key is set (sidebar or `.env`).
2. Toggle **Enable Quality Judge** on in the sidebar.
3. Click **Run Quality Judge** after generating the paper.

#### What the judge checks

| Criterion | What it detects |
|---|---|
| **Grammatical accuracy** | Grammar errors in the question text |
| **Clarity** | Ambiguous phrasing — more than one valid interpretation |
| **Difficulty alignment** | Whether the question actually matches Easy / Medium / Hard |
| **Language level** | Vocabulary and syntax appropriate for the stated difficulty |
| **Instruction clarity** | Whether the student knows exactly what is being asked |
| **Distractor quality** | MCQ only — plausible wrong options with one clear correct answer |
| **Format compliance** | Spelling, punctuation, structural errors |

#### Verdict rules

| Verdict | Meaning |
|---|---|
| **Pass** | Ready to use as-is |
| **Revise** | Needs minor corrections before use |
| **Fail** | Should not be used — major quality issue detected |

Hard override rules applied automatically:
- If **Clarity = Major Issue** → verdict forced to **Fail**
- If **Grammatical accuracy = Major Issue** → verdict forced to **Fail**
- If **Instruction clarity = Unclear** → verdict raised to at least **Revise**
- If **Distractor quality = Weak** (MCQ) → verdict raised to at least **Revise**

#### Reading the results

After judging, you see:

```
┌─────────────────────────────────────────────────┐
│  ✅ Pass: 7   ⚠️ Revise: 2   ❌ Fail: 1         │
│  Filter: [All] [Pass] [Revise] [Fail]           │
│                                                  │
│  ▼ Q1 [Easy MCQ] — What is the capital of...    │
│    ✅ Pass  `Q001`                               │
│    Grammatical accuracy: None                    │
│    Clarity:              None                    │
│    Difficulty alignment: Aligned                 │
│    ...                                           │
│    [✅ Confirm Pass] [⚠️ Mark Revise] [❌ Mark Fail] │
│                                                  │
│  ▼ Q8 [Hard Short Answer] — Explain why...      │
│    ❌ Fail  `Q016`                               │
│    Clarity: Major Issue                          │
│    💡 Suggestion: Specify the method of proof   │
│    ...                                           │
└─────────────────────────────────────────────────┘
```

Failed and Revised questions are expanded by default; passed questions are collapsed.

---

## Judge Optimization (DSPy + GEPA)

The judge prompt improves automatically over time as you collect feedback.

### How it works

```
User confirms / overrides each verdict
            ↓
Saved to data/judge_training.jsonl
            ↓
  5–19 examples:  BootstrapFewShot
            ↓     (adds best examples as few-shot demos)
 20+ examples:    GEPA
            ↓     (reflection LM rewrites the prompt itself)
Optimized artifact saved to artifacts/english_judge_optimized.json
            ↓
Next run loads the optimized prompt automatically
```

### Collecting feedback

After every judge run, each question card shows three buttons:

- **Confirm Pass** — you agree the question is fine.
- **Mark Revise** — you think it needs minor corrections.
- **Mark Fail** — you agree it should be removed.

Every click saves one labelled example to `data/judge_training.jsonl`.

### Running optimization

Once you have 5 or more labelled examples, the **Optimize Judge Prompt** button becomes active in the sidebar.

| Examples collected | Optimizer used | What it does |
|---|---|---|
| 5–19 | BootstrapFewShot | Adds the best examples as few-shot demonstrations in the prompt |
| 20+ | GEPA | Uses a reflection LM to rewrite the instruction prompt for better accuracy |

You can also run optimization from the command line:
```bash
python -m optimize.judge_optimizer           # auto-selects BootstrapFewShot or GEPA
python -m optimize.judge_optimizer --gepa    # force GEPA even with fewer examples
```

---

## Input File 1 — Word Template (.docx)

This is the question paper **skeleton** — it already contains all your headers, instructions, section titles, marks allocation, and formatting. Instead of actual questions, you place **placeholder tags** where questions should appear.

### Placeholder format

```
{{DIFFICULTY_QUESTIONTYPE}}
```

Each placeholder must be on its **own line** (nothing else in the same paragraph).

### Full placeholder reference

| Placeholder | What gets inserted |
|---|---|
| `{{EASY_MCQ}}` | Easy multiple-choice questions |
| `{{MEDIUM_MCQ}}` | Medium multiple-choice questions |
| `{{HARD_MCQ}}` | Hard multiple-choice questions |
| `{{EASY_SHORT_ANSWER}}` | Easy short-answer questions |
| `{{MEDIUM_SHORT_ANSWER}}` | Medium short-answer questions |
| `{{HARD_SHORT_ANSWER}}` | Hard short-answer questions |
| `{{EASY_LONG_ANSWER}}` | Easy long-answer / essay questions |
| `{{MEDIUM_LONG_ANSWER}}` | Medium long-answer / essay questions |
| `{{HARD_LONG_ANSWER}}` | Hard long-answer / essay questions |

### Count override

| Example | Behaviour |
|---|---|
| `{{EASY_MCQ}}` | Uses the form's Easy count |
| `{{EASY_MCQ_5}}` | Always inserts exactly 5, ignoring the form |
| `{{SECTION_A_MEDIUM_MCQ_3}}` | Prefix ignored; inserts 3 medium MCQ |

### Short aliases

| Alias | Equivalent to |
|---|---|
| `SA` | `SHORT_ANSWER` |
| `LA` | `LONG_ANSWER` |

`{{EASY_SA}}` = `{{EASY_SHORT_ANSWER}}`

### Template rules

- Each placeholder must be **alone in its own paragraph**.
- Placeholders are **case-insensitive** — `{{easy_mcq}}` and `{{EASY_MCQ}}` both work.
- All other content (headings, tables, instructions, footers) is preserved exactly.

### Example template layout

```
ANNUAL EXAMINATION 2025
Subject: English Grammar  |  Topic: Tenses

Instructions: Attempt all questions.

SECTION A — Multiple Choice  (1 mark each)
{{EASY_MCQ}}
{{MEDIUM_MCQ}}
{{HARD_MCQ}}

SECTION B — Short Answer  (3 marks each)
{{EASY_SHORT_ANSWER}}
{{MEDIUM_SHORT_ANSWER}}

SECTION C — Essay  (10 marks each)
{{HARD_LONG_ANSWER}}
```

---

## Input File 2 — Question Dataset (.csv or .xlsx)

Every row in the spreadsheet is one question.

### Required columns

| Column | Description | Example |
|---|---|---|
| `question_id` | Unique identifier | `Q001`, `ENG_045` |
| `topic` | Broad subject | `English Grammar` |
| `subtopic` | Narrower category | `Tenses` |
| `difficulty` | Difficulty level | `Easy`, `Medium`, `Hard` |
| `question_type` | Question format | `MCQ`, `Short Answer`, `Long Answer` |
| `question_text` | Full question body | `Choose the correct verb form…` |

### Optional columns

| Column | Description | Notes |
|---|---|---|
| `option_a` | MCQ option A | Required for MCQ rows |
| `option_b` | MCQ option B | Required for MCQ rows |
| `option_c` | MCQ option C | Required for MCQ rows |
| `option_d` | MCQ option D | Required for MCQ rows |
| `correct_answer` | `A`/`B`/`C`/`D` for MCQ, or answer text | Used by the judge for distractor quality check |
| `marks` | Per-question mark value | Informational only |

### Accepted difficulty values

| Input (case-insensitive) | Stored as |
|---|---|
| `Easy`, `Simple`, `Low` | `easy` |
| `Medium`, `Moderate` | `medium` |
| `Hard`, `Difficult`, `High` | `hard` |

### Accepted question_type values

| Input (case-insensitive) | Stored as |
|---|---|
| `MCQ`, `Multiple Choice` | `mcq` |
| `Short Answer`, `Short`, `SA`, `short_answer` | `short_answer` |
| `Long Answer`, `Long`, `LA`, `Essay`, `Descriptive` | `long_answer` |

### Sample rows

```csv
question_id,topic,subtopic,difficulty,question_type,question_text,option_a,option_b,option_c,option_d,correct_answer,marks
Q001,English Grammar,Tenses,Easy,MCQ,She ___ to school every day.,go,goes,going,gone,B,1
Q002,English Grammar,Tenses,Easy,Short Answer,Write the past tense form of the verb 'run'.,,,,,"ran",2
Q003,English Grammar,Tenses,Medium,MCQ,"By tomorrow, she ___ the report.","will finish","will have finished","has finished","had finished",B,1
Q004,English Grammar,Tenses,Hard,Long Answer,Explain the difference between Present Perfect and Past Simple tenses with five examples each.,,,,,See model answer,10
```

> **Tip:** Column names are case-insensitive and spaces are normalised, so `Question Text` and `question_text` are treated the same.

---

## Output File

The output `.docx` is your template with every `{{PLACEHOLDER}}` replaced by numbered, formatted questions.

### MCQ format

```
1. She ___ to school every day.
    (A)  go
    (B)  goes
    (C)  going
    (D)  gone

2. By tomorrow, she ___ the report.
    (A)  will finish
    (B)  will have finished
    ...
```

### Short Answer format

```
1. Write the past tense form of the verb 'run'.
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________
```

### Long Answer format

```
1. Explain the difference between Present Perfect and Past Simple tenses.
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________
```

---

## Sidebar Reference

| Sidebar section | Purpose |
|---|---|
| **Judge Settings** | Enter Mistral API key, choose model, toggle judge on/off |
| **Judge Optimization** | Shows example count, optimization status, Optimize button |
| **Placeholder Guide** | Quick reference for all placeholder names and aliases |

---

## Project File Structure

```
d:\Graded-Ass\
│
├── app.py                        ← Streamlit app — run this
├── requirements.txt              ← Python dependencies
├── create_sample_template.py     ← Run once to generate sample template
├── .env                          ← Your API keys (not committed to git)
├── .env.example                  ← Template — copy to .env and fill in
├── .gitignore
│
├── modules\
│   ├── dataset_loader.py         ← Load and validate CSV / Excel dataset
│   ├── template_parser.py        ← Scan .docx, extract {{PLACEHOLDER}} records
│   ├── question_selector.py      ← Filter questions, enforce no-duplicate rule
│   ├── paper_generator.py        ← XML-level Word replacement, BytesIO output
│   └── judge.py                  ← DSPy English quality judge (7 criteria)
│
├── optimize\
│   └── judge_optimizer.py        ← BootstrapFewShot / GEPA optimization script
│
├── data\
│   └── judge_training.jsonl      ← Grows as you confirm/override judge verdicts
│
├── artifacts\
│   └── english_judge_optimized.json  ← Written after optimization; auto-loaded by judge
│
└── sample_data\
    ├── questions.csv             ← 18 sample questions (Mathematics / Algebra)
    └── template.docx             ← Sample Word template with all 9 placeholders
```

---

## Requirements

```
streamlit>=1.32.0
python-docx>=1.1.0
pandas>=2.2.0
openpyxl>=3.1.2
lxml>=5.1.0
dspy-ai>=2.6.0
python-dotenv>=1.0.1
```

Python 3.8 or higher is required.

```bash
pip install -r requirements.txt
```

---

## Warnings and Edge Cases

| Situation | What happens |
|---|---|
| **Not enough questions in dataset** | All available questions inserted + note `[NOTE: Only N of M available]` appended in document |
| **Zero count for a difficulty** | Placeholder replaced with blank line |
| **Unrecognised placeholder** (e.g. `{{MY_TAG}}`) | Left untouched in document; warning shown in UI |
| **No placeholders found** | Document returned unchanged with a warning |
| **Duplicate questions** | Global ID tracking — a question never appears twice in the same paper |
| **Placeholder split by Word autocorrect** | Runs collapsed automatically before parsing; handled silently |
| **MCQ row missing options** | Rendered as `(A) [option not provided]`; warning shown in UI |
| **No Mistral API key** | Paper generation still works; judge step is simply disabled |
| **Judge JSON parse error** | Verdict defaults to Revise with raw output shown; never crashes the app |

---

## Common Issues

**"Dataset is missing required columns"**
: Check your spreadsheet has all 6 required columns: `question_id`, `topic`, `subtopic`, `difficulty`, `question_type`, `question_text`. Column names are case-insensitive.

**"0 questions placed"**
: The Topic or Subtopic you typed does not match anything in the dataset. Check for typos — spelling must be identical (though case is ignored).

**"No recognised placeholders found"**
: Make sure each placeholder is alone on its own line in the Word document and uses the exact format `{{DIFFICULTY_TYPE}}` with double curly braces. See the placeholder table above.

**Judge always returns Revise / Fail**
: The judge may be zero-shot without enough context. Confirm correct verdicts using the feedback buttons to build up `data/judge_training.jsonl`, then click **Optimize Judge Prompt** in the sidebar.

**"GEPA not available in this DSPy version"**
: Run `pip install --upgrade dspy-ai` to get the latest version. The optimizer automatically falls back to BootstrapFewShot if GEPA is unavailable.

**Excel file gives an error**
: Make sure the file is saved as `.xlsx`. Open in Excel and use *Save As → Excel Workbook (.xlsx)*.

**Download button does not appear**
: A generation error occurred. Look for the red error message above the Generate button.

---
name: anu-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in ANU (Annamacharya University) format. Trigger when the user
  mentions Annamacharya University, ANU mid exam, or requests a 2-part paper with
  Part A containing sub-questions (a, b, c, d, e) each mapped to a Course Outcome
  and Bloom's Level, and Part B containing long-answer questions with OR alternates.
  Also trigger when the user provides a Hall Ticket Number field, batch info like
  'II B.Tech I Semester – CSE & Allied Branches', or mentions condensed marks
  (e.g. '30 marks condensed to 25 marks'). Do NOT trigger for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# ANU Graded Assessment Skill

Generates a `.docx` Graded Assessment document in Annamacharya University format —
a 2-part mid-exam paper with a Hall Ticket number row, numbered notes, and a
6-column table layout (Q.No | sub | Question | | Course Outcomes | Bloom's Level).

---

## Core Workflow

1. **Collect inputs** — gather university name, batch, exam type, course name, date,
   duration, max marks, numbered notes, Part A sub-questions (a–e with CO and
   Bloom's level), and Part B questions with OR alternates, marks, CO, and Bloom's level.

2. **Validate question structure** — Part A must have exactly 5 sub-questions (a–e)
   under a single Q.1. Part B questions should alternate between a numbered question
   and an `(OR)` row. Marks per Part B question must be specified.

3. **Generate the document** — call `AnuAssessmentRequest` → `GradedAssessmentService().generate()`.
   The renderer builds: header block → Hall Ticket table → numbered notes →
   Part A 6-column table → Part B 6-column table.

4. **Verify output** — open or render the `.docx` to confirm:
   - University name and batch are bold and centred at the top
   - Hall Ticket table has 11 empty cells after the label
   - Notes are numbered (1. 2. 3. 4.)
   - Part A has Q.1 spanning the first column with sub-questions a)–e) below it
   - Part B (OR) rows span the full row width and are centred
   - CO and Bloom's level columns are populated for every question row

5. **Return the result** — provide the output file path from `GradedAssessmentResult.output_path`.

---

## Document Layout

```
        ANNAMACHARYA UNIVERSITY
  II B.Tech I Semester – CSE & Allied Branches
           IInd Mid Examination
        Professional Skills for Engineers

Date: 28-08-2025   Duration: 2Hrs   Max. Marks: 30

┌──────────────────────────────────────────────────────────────────┐
│ H.T. No:- │   │   │   │   │   │   │   │   │   │   │            │
└──────────────────────────────────────────────────────────────────┘

Note:
  1. Question Paper consists of two parts (Part-A and Part-B)
  2. In Part-A, each question carries one mark.
  3. 30 marks in Part-B will be condensed to 25 marks.
  4. Answer ALL the questions in Part-A and Part-B

┌──────┬─────┬──────────────────────────────┬──────┬───────────────┬─────────────┐
│PART-A│     │                              │      │Course Outcomes│ Bloom's     │
│      │     │ Answer all short answer Qs   │      │               │ level       │
├──────┼─────┼──────────────────────────────┼──────┼───────────────┼─────────────┤
│ 1    │ a)  │ Fill in the blanks …         │      │     CO1       │     L1      │
│      │ b)  │ Identify and correct the … │      │     CO1       │     L2      │
│      │ c)  │ Choose the option which …    │      │     CO1       │     L2      │
│      │ d)  │ Rearrange the jumbled …      │      │     CO1       │     L2      │
│      │ e)  │ Convert the sentence …       │      │     CO1       │     L1      │
└──────┴─────┴──────────────────────────────┴──────┴───────────────┴─────────────┘

┌──────┬─────┬──────────────────────────────┬──────┬───────────────┬─────────────┐
│PART B│     │                              │ Marks│Course Outcomes│ Bloom's     │
├──────┼─────┼──────────────────────────────┼──────┼───────────────┼─────────────┤
│ 2    │     │ Read the passage …           │      │               │             │
│      │     │ What does LiDAR help …       │  2M  │     CO4       │     L1      │
├──────┴─────┴──────────────────────────────┴──────┴───────────────┴─────────────┤
│                               (OR)                                              │
├──────┬─────┬──────────────────────────────┬──────┬───────────────┬─────────────┤
│ 3    │     │ Rearrange the sentences …    │ 10M  │     CO1       │     L2      │
└──────┴─────┴──────────────────────────────┴──────┴───────────────┴─────────────┘
```

---

## Bloom's Levels

| Code | Level      |
|------|-----------|
| L1   | Remember  |
| L2   | Understand|
| L3   | Apply     |
| L4   | Analyse   |
| L5   | Evaluate  |
| L6   | Create    |

---

## Input Shape

```python
AnuAssessmentRequest(
    university_id   = "anu",          # fixed — selects ANU renderer
    university_name = "ANNAMACHARYA UNIVERSITY",
    batch           = "II B.Tech I Semester – CSE & Allied Branches",
    exam_type       = "IInd Mid Examination",
    course_name     = "Professional Skills for Engineers",
    date            = "28-08-2025",
    duration        = "2Hrs",
    max_marks       = 30,
    notes = [
        "Question Paper consists of two parts (Part-A and Part-B)",
        "In Part-A, each question carries one mark.",
        "30 marks in Part-B will be condensed to 25 marks.",
        "Answer ALL the questions in Part-A and Part-B",
    ],
    part_a = AnuPartA(
        sub_questions = [
            AnuSubQuestion(sub="a)", text="Fill in the blanks …",       co="CO1", bloom="L1"),
            AnuSubQuestion(sub="b)", text="Identify and correct …",     co="CO1", bloom="L2"),
            AnuSubQuestion(sub="c)", text="Choose the option …",        co="CO1", bloom="L2"),
            AnuSubQuestion(sub="d)", text="Rearrange the jumbled …",    co="CO1", bloom="L2"),
            AnuSubQuestion(sub="e)", text="Convert the sentence …",     co="CO1", bloom="L1"),
        ],
    ),
    part_b = AnuPartB(
        questions = [
            AnuPartBQuestion(number="2",    text="Read the passage …",  marks="",    co="",    bloom=""),
            AnuPartBQuestion(number="",     text="What does LiDAR …",   marks="2M",  co="CO4", bloom="L1"),
            AnuPartBQuestion(number="(OR)", text="(OR)",                marks="",    co="",    bloom=""),
            AnuPartBQuestion(number="3",    text="Rearrange sentences", marks="10M", co="CO1", bloom="L2"),
        ],
    ),
)
```

---

## Output

- File saved to: `artifacts/graded-assessments/anu-assessment-{uid}.docx`
- Returns: `GradedAssessmentResult(output_path=..., university_id="anu")`
- Open in Microsoft Word or LibreOffice to review before sharing

---

## Validation Checklist

- [ ] University name bold and centred at top
- [ ] Hall Ticket row has 11 empty cells after the label
- [ ] Notes are numbered 1–4
- [ ] Part A: Q.1 spans first column; sub-questions a)–e) fill rows below
- [ ] CO column populated for every Part A sub-question
- [ ] Bloom's level column populated for every Part A sub-question
- [ ] Part B (OR) rows span full width and are centred
- [ ] Part B marks, CO, and Bloom's Level filled for every question

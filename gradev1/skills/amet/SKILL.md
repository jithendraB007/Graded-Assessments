---
name: amet-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in AMET (Academy of Maritime Education and Training) university format.
  Trigger when the user mentions AMET, maritime university assessment, or requests
  a question paper with Part A (MCQ), Part B (long answer with OR options), and
  Part C (case study). Also trigger when the user provides course details like
  Programme & Batch, Course Code, BTL levels (K1–K6), and CO mappings (CO1–CO5)
  for an AMET paper. Do NOT trigger for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# AMET Graded Assessment Skill

Generates a `.docx` Graded Assessment document in AMET university format — a 3-part
question paper with a 5-column table (Question No | Question | Mark | BTL | CO).

---

## Core Workflow

1. **Collect inputs** — gather all required fields: exam type, programme, semester,
   course name, course code, duration, max marks, instructions, and all questions
   with their BTL and CO values.

2. **Validate question structure** — ensure Part A questions have individual marks,
   Part B has paired OR questions (21a/21b … 25a/25b), and Part C has exactly one
   case study question. Total marks must equal `max_marks`.

3. **Generate the document** — call `AmetAssessmentRequest` → `GradedAssessmentService().generate()`.
   The renderer builds: header block → instructions → 5-column table with Part A / Part B (with OR rows) / Part C.

4. **Verify output** — open or render the `.docx` to confirm:
   - Header lines are right-aligned with correct spacing
   - Table has 5 columns throughout (Question No, Question, Mark, BTL, CO)
   - Part A rows are individual, Part B rows come in a/b pairs separated by centred "(OR)" rows
   - Part C is a single merged row followed by one question row
   - Total marks in headers match the sum of individual question marks

5. **Return the result** — provide the output file path from `GradedAssessmentResult.output_path`.

---

## Document Layout

```
MODEL EXAMINATIONS – APRIL 2026
Programme & Batch: B.Tech SE/CSE          Semester: II
Course Name: Communicative English        Course Code: 256EN1A22TD
Duration: 3 hours                         Maximum Marks: 100 marks

Instructions:
  1. Before attempting any question paper, ensure you have received the correct paper.
  2. The missing data, if any, may be assumed suitably.

┌────────────┬──────────────────────────────────────┬──────┬─────┬─────┐
│ Question No│ Question                             │ Mark │ BTL │ CO  │
├────────────┴──────────────────────────────────────┴──────┴─────┴─────┤
│       PART A (20×1 = 20 Marks)  Answer all the questions             │
├────────────┬──────────────────────────────────────┬──────┬─────┬─────┤
│ 1          │ Choose the correct option …          │  1   │ K2  │ CO1 │
│ 2          │ Identify the word similar in …       │  1   │ K2  │ CO1 │
│  …                                                                    │
├────────────┴──────────────────────────────────────┴──────┴─────┴─────┤
│       PART B (5×14 = 70 Marks)  Answer all the questions             │
├────────────┬──────────────────────────────────────┬──────┬─────┬─────┤
│ 21 (a)     │ Write a paragraph of 200 words …     │ 14   │ K6  │ CO1 │
│            │                (OR)                  │      │     │     │
│ 21 (b)     │ Write a paragraph about …            │ 14   │ K6  │ CO1 │
│  …                                                                    │
├────────────┴──────────────────────────────────────┴──────┴─────┴─────┤
│       PART C (1×10 = 10 Marks)  Answer the Question                  │
├────────────┬──────────────────────────────────────┬──────┬─────┬─────┤
│ 26         │ Read the case study and answer …     │ 10   │K3-K5│ CO5 │
└────────────┴──────────────────────────────────────┴──────┴─────┴─────┘
```

---

## BTL Levels

| Code | Bloom's Level |
|------|--------------|
| K1   | Remember     |
| K2   | Understand   |
| K3   | Apply        |
| K4   | Analyse      |
| K5   | Evaluate     |
| K6   | Create       |

---

## Input Shape

```python
AmetAssessmentRequest(
    university_id = "amet",          # fixed — selects AMET renderer
    exam_type     = "MODEL EXAMINATIONS – APRIL 2026",
    programme     = "B.Tech SE/CSE",
    semester      = "II",
    course_name   = "Communicative English Advanced",
    course_code   = "256EN1A22TD",
    duration      = "3 hours",
    max_marks     = 100,
    instructions  = [
        "Before attempting any question paper, ensure that you have received the correct paper.",
        "The missing data, if any, may be assumed suitably.",
    ],
    part_a = AmetPartA(
        total       = "20×1 = 20 Marks",
        instruction = "Answer all the questions",
        questions   = [
            AmetQuestion(number="1", text="Choose the correct option …", mark=1, btl="K2", co="CO1"),
            # … 20 questions total
        ],
    ),
    part_b = AmetPartB(
        total           = "5×14 = 70 Marks",
        instruction     = "Answer all the questions",
        question_pairs  = [
            AmetQuestionPair(
                a = AmetQuestion(number="21 (a)", text="Write a paragraph …", mark=14, btl="K6", co="CO1"),
                b = AmetQuestion(number="21 (b)", text="Write an essay …",   mark=14, btl="K6", co="CO1"),
            ),
            # … 5 pairs total (21–25)
        ],
    ),
    part_c = AmetPartC(
        total       = "1×10 = 10 Marks",
        instruction = "Answer the Question",
        question    = AmetQuestion(number="26", text="Read the case study …", mark=10, btl="K3-K5", co="CO5"),
    ),
)
```

---

## Output

- File saved to: `artifacts/graded-assessments/amet-assessment-{uid}.docx`
- Returns: `GradedAssessmentResult(output_path=..., university_id="amet")`
- Open in Microsoft Word or LibreOffice to review before sharing

---

## Validation Checklist

- [ ] Header: all 4 lines present (exam type, programme/semester, course/code, duration/marks)
- [ ] Instructions numbered correctly
- [ ] Table has exactly 5 columns throughout
- [ ] Part A: individual question rows, no OR separators
- [ ] Part B: each pair has an "(OR)" row centred between `a` and `b`
- [ ] Part C: single merged section header + one question row
- [ ] Sum of all marks = `max_marks`
- [ ] All BTL values are K1–K6; all CO values are CO1–CO5

---
name: s-vyasa-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in S-VYASA (Swami Vivekananda Yoga Anusandhana Samsthana) university
  format. Trigger when the user mentions S-VYASA, SVYASA, or requests a 2-part
  paper with Part A (10 questions × 3 marks = 30) and Part B (5 question pairs
  × 14 marks = 70) using a 5-column table (Q.No | Questions | CO | RBTL | Marks)
  with a USN (University Seat Number) header row and a structured header table
  containing month/year, program, semester, and course details. Do NOT trigger
  for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# S-VYASA Graded Assessment Skill

Generates a `.docx` Graded Assessment document in S-VYASA university format —
a 2-part paper with a USN row, a 4-column header metadata table, and 5-column
question tables (Q.No | Questions | CO | RBTL | Marks) for both parts.

---

## Core Workflow

1. **Collect inputs** — gather month/year, academic year, program, specialization,
   semester, date of exam, course code, course name, all Part A questions (with CO
   and RBTL), and all Part B question pairs (each pair has an `a` and `b` question).

2. **Validate question structure** — Part A must have exactly 10 questions, each
   worth 3 marks (total 30). Part B must have exactly 5 question pairs, each worth
   14 marks (total 70). All questions need CO and RBTL values.

3. **Generate the document** — call `SvyasaAssessmentRequest` → `GradedAssessmentService().generate()`.
   The renderer builds: USN table → header metadata table → Part A section header +
   5-column table → Part B section header + 5-column table with OR rows between pairs.

4. **Verify output** — open or render the `.docx` to confirm:
   - USN table appears first with 11 empty cells after the "USN" label
   - Header metadata table has 4 columns and 5 rows (month/year, program, semester, course code, course name)
   - "Part – A" and "Part - B" headings are centred and bold
   - Part A/B description lines show the correct formula (e.g. "10 Q x 3 M = 30")
   - Part B question pairs are separated by centred "(OR)" rows that span all 5 columns
   - CO and RBTL columns filled for every question row

5. **Return the result** — provide the output file path from `GradedAssessmentResult.output_path`.

---

## Document Layout

```
┌─────┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ USN │   │   │   │   │   │   │   │   │   │   │
└─────┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

┌──────────────────────────────┬────────────────┬─────────────────┬────────────┐
│ Month & Year of Examination  │  July 2025     │  Academic year  │  2024-25   │
│ Program                      │  B. Tech       │  Specialization │  All       │
│ Semester                     │  1             │  Date of Exam   │            │
│ Course Code                  │  ENGL105       │  ENGL105        │  ENGL105   │
│ Course Name                  │  English LSRW  │  English LSRW   │ English    │
└──────────────────────────────┴────────────────┴─────────────────┴────────────┘

                          Part – A
           Answer all the questions      10 Q x 3 M = 30

┌────────┬──────────────────────────────────────────┬─────┬──────┬───────┐
│ Q.No.  │ Questions                                │ CO  │ RBTL │ Marks │
├────────┼──────────────────────────────────────────┼─────┼──────┼───────┤
│ 1.     │ Choose the correct collective noun …     │  5  │  1   │   3   │
│ 2.     │ Write two sentences using the word …     │  2  │  2   │   3   │
│ …      │ …  (10 questions total)                  │     │      │       │
└────────┴──────────────────────────────────────────┴─────┴──────┴───────┘

                          Part - B
           Answer all the questions       5 Q x 14 M = 70

┌────────┬──────────────────────────────────────────┬─────┬──────┬───────┐
│ Q.No.  │ Questions                                │ CO  │ RBTL │ Marks │
├────────┼──────────────────────────────────────────┼─────┼──────┼───────┤
│ 11a.   │ Read the passage and answer …            │  2  │  4   │  14   │
├────────┴──────────────────────────────────────────┴─────┴──────┴───────┤
│                              OR                                         │
├────────┬──────────────────────────────────────────┬─────┬──────┬───────┤
│ 11b.   │ Read the passage carefully and answer …  │  5  │  4   │  14   │
│ …      │ …  (5 pairs total)                       │     │      │       │
└────────┴──────────────────────────────────────────┴─────┴──────┴───────┘
```

---

## RBTL Levels (Revised Bloom's Taxonomy)

| Code | Level      |
|------|-----------|
| 1    | Remember  |
| 2    | Understand|
| 3    | Apply     |
| 4    | Analyse   |
| 5    | Evaluate  |
| 6    | Create    |

---

## Input Shape

```python
SvyasaAssessmentRequest(
    university_id = "s-vyasa",      # fixed — selects S-VYASA renderer
    month_year    = "July 2025",
    academic_year = "2024-25",
    program       = "B. Tech",
    specialization= "All",
    semester      = "1",
    date_of_exam  = "",
    course_code   = "ENGL105",
    course_name   = "English LSRW",
    part_a = SvyasaPartA(
        questions = [
            SvyasaQuestion(number="1.",  text="Choose the correct collective noun …", co="5", rbtl="1", marks=3),
            SvyasaQuestion(number="2.",  text="Write two sentences using 'impact' …", co="2", rbtl="2", marks=3),
            # … 10 questions total
        ],
    ),
    part_b = SvyasaPartB(
        question_pairs = [
            SvyasaQuestionPair(
                a = SvyasaQuestion(number="11a.", text="Read the passage and answer …",         co="2", rbtl="4", marks=14),
                b = SvyasaQuestion(number="11b.", text="Read the passage carefully and answer …",co="5", rbtl="4", marks=14),
            ),
            # … 5 pairs total (11–15)
        ],
    ),
)
```

---

## Output

- File saved to: `artifacts/graded-assessments/s-vyasa-assessment-{uid}.docx`
- Returns: `GradedAssessmentResult(output_path=..., university_id="s-vyasa")`
- Open in Microsoft Word or LibreOffice to review before sharing

---

## Validation Checklist

- [ ] USN row appears first with 11 empty cells
- [ ] Header metadata table has 5 rows × 4 columns
- [ ] "Part – A" heading centred and bold
- [ ] Part A description line shows correct formula: `10 Q x 3 M = 30`
- [ ] Part A table has exactly 10 question rows
- [ ] "Part - B" heading centred and bold
- [ ] Part B description line shows correct formula: `5 Q x 14 M = 70`
- [ ] Part B OR rows span all 5 columns and are centred
- [ ] Part B has exactly 5 question pairs (10 question rows + 5 OR rows)
- [ ] CO and RBTL columns populated for every question row
- [ ] All marks in Part A = 3; all marks in Part B = 14

---
name: s-vyasa-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in S-VYASA (Swami Vivekananda Yoga Anusandhana Samsthana) university
  format. Trigger when the user mentions S-VYASA, SVYASA, or requests a two-part
  paper with Part A carrying ten questions worth three marks each totalling thirty
  marks, and Part B carrying five question pairs worth fourteen marks each totalling
  seventy marks. The document has a University Seat Number row at the top and a
  four-column header metadata table. Questions use a five-column table with columns
  for Q.No, Questions, CO, RBTL, and Marks. Do NOT trigger for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# S-VYASA Graded Assessment Skill

This skill generates a Graded Assessment Word document in S-VYASA university format.
It uses the university template from `assets/templates/S-Vyasa.docx` as the base
and inserts the university logo from `assets/logos/s-vyasa.png` at the top of
the document.

---

## How the Document is Generated

The generation follows these steps:

First, the S-VYASA template file is opened from `assets/templates/S-Vyasa.docx`.
This preserves the university's page layout, margins, and fonts. The template
content is cleared so new questions can be written in cleanly.

Next, the university logo is placed at the top of the page, centred, using the
image file at `assets/logos/s-vyasa.png`.

A University Seat Number row is written first — a table with one label cell on
the left and eleven empty cells to the right where students write their seat number.

Below that, a four-column header metadata table is written with five rows covering
the month and year of examination, academic year, program, specialisation, semester,
date of examination, course code, and course name.

The Part A section follows. The heading "Part – A" is written centred and bold,
followed by a line showing the marks formula such as "10 Q x 3 M = 30". The
questions are laid out in a five-column table with the column headers Q.No,
Questions, CO, RBTL, and Marks. Each of the ten questions occupies one row.

The Part B section follows the same pattern. The heading "Part - B" is written
centred and bold, followed by the marks formula such as "5 Q x 14 M = 70". The
five question pairs are laid out in the same five-column table. Each pair has an
(a) question row and a (b) question row, separated by a full-width merged OR row.

The finished document is saved to `artifacts/graded-assessments/` and the file
path is returned.

---

## Template and Logo

Template file : `assets/templates/S-Vyasa.docx`
Logo file     : `assets/logos/s-vyasa.png`

If the logo file is not present the document is still generated without a logo.
To add or update the logo, place a PNG image named `s-vyasa.png` inside the
`assets/logos/` folder before running the skill.

---

## Document Structure

The document opens with the USN row for seat number entry, followed by the
header metadata table that identifies the exam, course, and semester.

Part A contains ten questions each worth three marks, totalling thirty marks.
Every question carries a Course Outcome number and an RBTL level. Students
answer all ten questions.

Part B contains five question pairs each worth fourteen marks, totalling seventy
marks. Students answer all five pairs, choosing either option (a) or option (b)
from each pair. Each question in Part B carries a Course Outcome number and an
RBTL level.

---

## What Information to Collect

Before generating the document, the following information must be gathered from
the user:

The month and year of the examination, the academic year, the program name, the
specialisation, the semester number, the date of examination if known, the course
code, and the course name.

For Part A, ten questions each with the question number, the full question text,
the Course Outcome number, the RBTL level, and the mark value (three for each).

For Part B, five question pairs where each pair has an (a) question and a (b)
question. Each question needs the question number, the full question text, the
Course Outcome number, the RBTL level, and the mark value (fourteen for each).

---

## RBTL Reference

1 is Remember. 2 is Understand. 3 is Apply. 4 is Analyse. 5 is Evaluate.
6 is Create.

---

## After Generation

Open the file from `artifacts/graded-assessments/` in Microsoft Word or LibreOffice
to review the layout. Confirm that the USN row is present, that the header metadata
table has five rows, that Part A has ten question rows, and that Part B has five
question pairs with OR rows between each pair. Check that CO and RBTL columns are
filled for every question.

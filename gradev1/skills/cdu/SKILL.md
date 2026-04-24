---
name: cdu-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in CDU (Chaitanya Deemed University) format. Trigger when the user
  mentions Chaitanya university, CDU, or requests a multi-set paper with Set A,
  Set B, and Set C variants. Each set has Section A with ten short questions where
  students answer any six, and Section B with long-answer question pairs separated
  by OR where students answer any two. CDU papers use a two-column layout with no
  CO or BTL columns. Do NOT trigger for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# CDU Graded Assessment Skill

This skill generates a Graded Assessment Word document in Chaitanya Deemed
University format. It uses the university template from `assets/templates/CDU.docx`
as the base and inserts the university logo from `assets/logos/cdu.png` at the
top of the document.

---

## How the Document is Generated

The generation follows these steps:

First, the CDU template file is opened from `assets/templates/CDU.docx`. This
preserves the university's page layout, margins, and fonts. The template content
is cleared so new questions can be written in cleanly.

Next, the university logo is placed at the top of the page, centred, using the
image file at `assets/logos/cdu.png`.

The document is then built as three back-to-back question sets — Set A, Set B,
and Set C — each starting on a new page. Every set is rendered as a single
two-column table. The first column carries the question number and the second
column carries the question text.

Each set begins with a merged full-width header row showing the set label,
the university name, and the course information. Below that, the time and
maximum marks appear on a split row — time on the left and marks on the right.

Section A follows with its instruction "Answer any six Questions" in a merged
row, and then ten numbered short questions.

Section B follows with its instruction "Answer the following Questions" in a
merged row, and then the question pairs. Between every pair, a full-width merged
OR row separates the two options.

The finished document is saved to `artifacts/graded-assessments/` and the file
path is returned.

---

## Template and Logo

Template file : `assets/templates/CDU.docx`
Logo file     : `assets/logos/cdu.png`

If the logo file is not present the document is still generated without a logo.
To add or update the logo, place a PNG image named `cdu.png` inside the
`assets/logos/` folder before running the skill.

---

## Document Structure

Each set follows the same layout. Section A contains ten short grammar and writing
questions. Students choose any six to answer. There are no mark allocations per
question and no Course Outcome or BTL columns.

Section B contains question pairs where each pair offers two long-answer options
separated by OR. Students answer any two questions from Section B in total.
Questions carry mark values stated in the exam instructions.

All three sets — A, B, and C — contain different questions on the same topics,
so each student in the exam hall receives a different variant.

---

## What Information to Collect

Before generating the document, the following information must be gathered from
the user:

The university name, the course information line, the time allowed, and the
maximum marks.

For each of the three sets — Set A, Set B, and Set C — a list of ten Section A
questions, each with a question number and the question text.

For each set, a list of Section B question pairs where each pair has an (a)
question and a (b) question, each with a number and question text.

---

## After Generation

Open the file from `artifacts/graded-assessments/` in Microsoft Word or LibreOffice
to review the layout. Confirm that all three sets are present, that each set starts
on a new page, that Section A has ten questions and Section B has pairs with OR
rows between them, and that no CO or BTL columns appear anywhere.

---
name: anu-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in ANU (Annamacharya University) format. Trigger when the user
  mentions Annamacharya University, ANU mid exam, or requests a two-part paper
  where Part A has five sub-questions labelled a through e under a single question
  number, and Part B has long-answer questions with OR alternates. Also trigger
  when the user provides details such as Hall Ticket Number fields, a batch
  description like 'II B.Tech I Semester – CSE and Allied Branches', or a note
  about condensed marks. Do NOT trigger for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# ANU Graded Assessment Skill

This skill generates a Graded Assessment Word document in Annamacharya University
format. It uses the university template from `assets/templates/ANU.docx` as the
base.

---

## How the Document is Generated

The generation follows these steps:

First, the ANU template file is opened from `assets/templates/ANU.docx`. This
preserves the university's page layout, margins, and fonts. The template content
is cleared so new questions can be written in cleanly.

The header block is written with the university name in large bold text centred
on the first line, followed by the batch and semester details, the exam type,
and the course name — all centred. The date, duration, and maximum marks appear
on a single line below.

A Hall Ticket Number row follows, made up of a table with eleven empty cells
where students write their registration number digit by digit.

Numbered notes appear next, listing the exam rules such as the number of parts,
marks per question, and condensed marking instructions.

The Part A questions are laid out in a six-column table. The heading row spans
the first four columns with the label PART-A, and the last two columns carry the
headings Course Outcomes and Bloom's level. Below the heading there is an
instruction row, then a row for Question 1, and then five sub-question rows
labelled a through e. Each sub-question row shows the sub-label, the question
text, the Course Outcome, and the Bloom's level.

The Part B questions follow in a separate six-column table with the headings
PART B, Marks, Course Outcomes, and Bloom's Level. Questions with OR alternates
are separated by a full-width merged OR row.

The finished document is saved to `artifacts/graded-assessments/` and the file
path is returned.

---

## Template

Template file : `assets/templates/ANU.docx`

---

## Document Structure

Part A carries five marks total from five sub-questions under Question 1. Each
sub-question is labelled a, b, c, d, and e. Each carries one mark and is mapped
to a Course Outcome and a Bloom's level.

Part B carries the remaining marks from long-answer questions. Questions that
have an OR alternate are paired with a full-width OR separator row so students
can choose. Marks for each Part B question are stated in the Marks column and
may be condensed to a lower value as stated in the notes.

---

## What Information to Collect

Before generating the document, the following information must be gathered from
the user:

The university name, the batch and semester description, and the exam type such
as "IInd Mid Examination".

The course name, the exam date, the duration, and the maximum marks.

Up to four numbered notes that explain the exam rules.

For Part A, five sub-questions each with their text, Course Outcome, and
Bloom's level.

For Part B, a list of question entries. Each entry is either a numbered question
with its marks, Course Outcome, and Bloom's level, or an OR separator row, or a
continuation question below a passage or set of sub-items.

---

## Bloom's Level Reference

L1 is Remember. L2 is Understand. L3 is Apply. L4 is Analyse. L5 is Evaluate.
L6 is Create.

---

## After Generation

Open the file from `artifacts/graded-assessments/` in Microsoft Word or LibreOffice
to review the layout. Confirm that the Hall Ticket row is present, that the Part A
table shows five sub-questions under Question 1, and that OR rows appear at the
correct positions in Part B.

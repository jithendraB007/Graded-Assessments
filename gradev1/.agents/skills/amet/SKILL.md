---
name: amet-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in AMET (Academy of Maritime Education and Training) university format.
  Trigger when the user mentions AMET, maritime university assessment, or requests
  a three-part question paper with Part A for multiple choice, Part B for long
  answer with OR options, and Part C for a case study. Also trigger when the user
  provides details such as Programme and Batch, Course Code, BTL levels, and CO
  mappings. Do NOT trigger for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# AMET Graded Assessment Skill

This skill generates a Graded Assessment Word document in AMET university format.
It uses the university template from `assets/templates/AMET.docx` as the base and
inserts the university logo from `assets/logos/amet.png` at the top of the document.

---

## How the Document is Generated

The generation follows these steps:

First, the AMET template file is opened from `assets/templates/AMET.docx`. This
preserves the university's page layout, margins, and fonts. The template content
is cleared so new questions can be written in cleanly.

Next, the university logo is placed at the top of the page, centred, using the
image file at `assets/logos/amet.png`.

The header block is then written with the exam type on the first line, followed
by the programme and semester details, the course name and course code, and finally
the duration and maximum marks — all matching the AMET house style.

A numbered list of exam instructions follows the header.

The questions are laid out in a five-column table with the headings Question No,
Question, Mark, BTL, and CO. The table is divided into three clearly labelled
sections — Part A, Part B, and Part C — each introduced by a full-width merged
header row showing the marks formula and the attempt instruction.

In Part A, each question occupies one row. In Part B, every question pair is
separated by a centred OR row so students can choose between option (a) and
option (b). Part C contains a single case study question worth ten marks.

The finished document is saved to `artifacts/graded-assessments/` and the file
path is returned.

---

## Template and Logo

Template file : `assets/templates/AMET.docx`
Logo file     : `assets/logos/amet.png`

If the logo file is not present the document is still generated without a logo.
To add or update the logo, place a PNG image named `amet.png` inside the
`assets/logos/` folder before running the skill.

---

## Document Structure

The document has three parts inside one continuous question table.

Part A carries twenty marks from twenty short questions worth one mark each.
Each question is tagged with a BTL level (K1 through K6) and a Course Outcome
(CO1 through CO5).

Part B carries seventy marks from five question pairs worth fourteen marks each.
Each pair presents an (a) option and a (b) option separated by an OR row. Students
attempt all five pairs, choosing one option from each pair.

Part C carries ten marks from one case study question. The case study is a
multi-part scenario with sub-questions carrying four, three, and three marks.

---

## What Information to Collect

Before generating the document, the following information must be gathered from
the user:

The exam type and month such as "MODEL EXAMINATIONS – APRIL 2026".

The programme name and batch such as "B.Tech SE/CSE" and the semester number.

The course name and its alphanumeric course code.

The exam duration in hours and the maximum marks, which is typically 100.

Up to four exam instructions that appear as numbered rules below the header.

For Part A, twenty questions each with their text, mark value, BTL level, and CO.

For Part B, five question pairs where each pair has an (a) option and a (b) option,
both with their text, fourteen marks, BTL level, and CO.

For Part C, one case study question with sub-questions totalling ten marks.

---

## BTL Reference

K1 is Remember. K2 is Understand. K3 is Apply. K4 is Analyse. K5 is Evaluate.
K6 is Create.

---

## After Generation

Open the file from `artifacts/graded-assessments/` in Microsoft Word or LibreOffice
to review the layout. Confirm that all three parts are present, that OR rows appear
correctly in Part B, and that the total of all question marks equals the maximum marks
stated in the header.

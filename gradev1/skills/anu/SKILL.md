---
name: anu-assessment-doc
description: "Use this skill to generate a Graded Assessment Word document in ANU
  (Annamacharya University) format. Trigger when the user mentions Annamacharya
  University, ANU mid exam, or requests a 2-part paper with Part A (sub-questions
  a-e) and Part B (long answer with OR). Produces a .docx with a 6-column table
  (Q.No | sub | Question | text | Course Outcomes | Bloom's Level) and a Hall Ticket
  number field."
license: Proprietary
---

# ANU Assessment Skill

## Document layout
- **Header:** University name, Semester & Branch, Exam type, Course name, Date, Duration, Max Marks
- **Hall Ticket No.** — fill-in row
- **Notes** — numbered instructions
- **Part A** — 5 sub-questions (a–e) under Q.1; columns: sub | Question | CO | Bloom's Level
- **Part B** — numbered questions with OR alternates; columns: Q.No | Question | Marks | CO | Bloom's Level

## Bloom's levels
L1 Remember, L2 Understand, L3 Apply, L4 Analyse, L5 Evaluate, L6 Create

## Input shape
```json
{
  "university_name": "ANNAMACHARYA UNIVERSITY",
  "batch": "II B.Tech I Semester – CSE & Allied Branches",
  "exam_type": "IInd Mid Examination",
  "course_name": "Professional Skills for Engineers",
  "date": "28-08-2025",
  "duration": "2Hrs",
  "max_marks": 30,
  "notes": [
    "Question Paper consists of two parts (Part-A and Part-B)",
    "In Part-A, each question carries one mark."
  ],
  "part_a": {
    "sub_questions": [
      {"sub": "a)", "text": "Question text", "co": "CO1", "bloom": "L1"},
      {"sub": "b)", "text": "Question text", "co": "CO1", "bloom": "L2"}
    ]
  },
  "part_b": {
    "questions": [
      {"number": "2", "text": "Question text", "marks": "10 M", "co": "CO2", "bloom": "L4"},
      {"number": "(OR)", "text": "(OR)", "marks": "", "co": "", "bloom": ""},
      {"number": "3", "text": "Question text", "marks": "10 M", "co": "CO2", "bloom": "L4"}
    ]
  }
}
```

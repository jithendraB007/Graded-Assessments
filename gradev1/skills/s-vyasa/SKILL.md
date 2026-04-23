---
name: s-vyasa-assessment-doc
description: "Use this skill to generate a Graded Assessment Word document in
  S-VYASA (Swami Vivekananda Yoga Anusandhana Samsthana) university format.
  Trigger when the user mentions S-VYASA, SVYASA, or requests a 2-part paper
  with Part A (10Q × 3M = 30) and Part B (5Q × 14M = 70) using a 5-column
  question table (Q.No | Questions | CO | RBTL | Marks) with a USN header row."
license: Proprietary
---

# S-VYASA Assessment Skill

## Document layout
- **USN row** — University Seat Number fill-in table
- **Header table:** Month & Year, Academic Year, Program, Specialization, Semester, Date, Course Code, Course Name
- **Part A** — 10 questions × 3 marks = 30; columns: Q.No | Questions | CO | RBTL | Marks
- **Part B** — 5 question pairs with OR; columns: Q.No | Questions | CO | RBTL | Marks

## RBTL levels (Revised Bloom's Taxonomy Levels)
1 Remember, 2 Understand, 3 Apply, 4 Analyse, 5 Evaluate, 6 Create

## Input shape
```json
{
  "month_year": "July 2025",
  "academic_year": "2024-25",
  "program": "B. Tech",
  "specialization": "All",
  "semester": "1",
  "date_of_exam": "",
  "course_code": "ENGL105",
  "course_name": "English LSRW",
  "part_a": {
    "questions": [
      {"number": "1.", "text": "Question text", "co": "5", "rbtl": "1", "marks": 3}
    ]
  },
  "part_b": {
    "question_pairs": [
      {
        "a": {"number": "11a.", "text": "Question text", "co": "2", "rbtl": "4", "marks": 14},
        "b": {"number": "11b.", "text": "Question text", "co": "5", "rbtl": "4", "marks": 14}
      }
    ]
  }
}
```

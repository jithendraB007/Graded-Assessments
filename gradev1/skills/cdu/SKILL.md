---
name: cdu-assessment-doc
description: "Use this skill to generate a Graded Assessment Word document in CDU
  (Chaitanya Deemed University) format. Trigger when the user mentions Chaitanya
  university, CDU, or requests a multi-set paper (Set A, Set B, Set C) with
  Section A (short questions, answer any 6) and Section B (long answer with OR).
  Produces a .docx with a 2-column layout (Q.No | Question) and no CO/BTL columns."
license: Proprietary
---

# CDU Assessment Skill

## Document layout
- **Header (per set):** Set label (Set-A / Set-B / Set-C), University name, Course info, Time, Max Marks
- **Section A** — 10 short questions, instruction: "Answer any six Questions"
- **Section B** — 4 long-answer questions with OR pairs, instruction: "Answer the following Questions"
- Each set is a separate 2-column table: Q.No | Question text

## Sets
CDU papers always have 3 sets (A, B, C) with different question variants.

## Input shape
```json
{
  "university_name": "CHAITANYA (DEEMED TO BE UNIVERSITY)",
  "course_info": "B.Tech – CSE – English",
  "time": "1½ Hrs",
  "max_marks": 50,
  "sets": [
    {
      "label": "Set - A",
      "section_a": {
        "instruction": "Answer any six Questions.",
        "questions": [
          {"number": "1.", "text": "Question text"},
          {"number": "2.", "text": "Question text"}
        ]
      },
      "section_b": {
        "instruction": "Answer the following Questions.",
        "question_pairs": [
          {
            "a": {"number": "11", "text": "Question text"},
            "b": {"number": "12", "text": "Question text"}
          }
        ]
      }
    }
  ]
}
```

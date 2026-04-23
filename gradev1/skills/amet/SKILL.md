---
name: amet-assessment-doc
description: "Use this skill to generate a Graded Assessment Word document in AMET
  (Academy of Maritime Education and Training) university format. Trigger when the
  user mentions AMET, maritime university, or requests a 3-part exam paper with
  Part A (MCQ), Part B (essay with OR), and Part C (case study). Produces a .docx
  with a 5-column question table (Question No | Question | Mark | BTL | CO)."
license: Proprietary
---

# AMET Assessment Skill

## Document layout
- **Header:** Exam type, Programme & Batch, Course Name, Course Code, Duration, Max Marks
- **Instructions:** bullet list of exam rules
- **Part A** — MCQ/short, each question has: Q.No | Question | Mark | BTL | CO
- **Part B** — Long answer with OR pairs: 21(a)/(b), 22(a)/(b) … 25(a)/(b)
- **Part C** — Case study (single question, 10 marks)

## BTL levels
K1 Remember, K2 Understand, K3 Apply, K4 Analyse, K5 Evaluate, K6 Create

## Input shape
```json
{
  "exam_type": "MODEL EXAMINATIONS – APRIL 2026",
  "programme": "B.Tech SE/CSE",
  "semester": "II",
  "course_name": "Communicative English Advanced",
  "course_code": "256EN1A22TD",
  "duration": "3 hours",
  "max_marks": 100,
  "instructions": [
    "Before attempting any question paper, ensure that you have received the correct question paper.",
    "The missing data, if any, may be assumed suitably."
  ],
  "part_a": {
    "total": "20×1 = 20 Marks",
    "instruction": "Answer all the questions",
    "questions": [
      {"number": "1", "text": "Question text", "mark": 1, "btl": "K2", "co": "CO1"}
    ]
  },
  "part_b": {
    "total": "5×14 = 70 Marks",
    "instruction": "Answer all the questions",
    "question_pairs": [
      {
        "a": {"number": "21 (a)", "text": "Question text", "mark": 14, "btl": "K6", "co": "CO1"},
        "b": {"number": "21 (b)", "text": "Question text", "mark": 14, "btl": "K6", "co": "CO1"}
      }
    ]
  },
  "part_c": {
    "total": "1×10 = 10 Marks",
    "instruction": "Answer the Question",
    "question": {"number": "26", "text": "Case study question", "mark": 10, "btl": "K3-K5", "co": "CO5"}
  }
}
```

---
name: graded-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document (.docx) needs
  to be created for a university course. Trigger when the user mentions: graded assessment,
  question paper, exam document, mid-term, end-term, or .docx for a university.
  Produces a structured Word document with Cover Page, Instructions, and section-wise
  Questions (MCQ, Short Answer, Long Answer, Fill-in-the-blank). Requires: university_id,
  cover page data (university_name, department, course_name, assessment_title, semester,
  date), instructions (duration, total_marks, passing_marks, attempt_rules, general_notes),
  and sections with questions (each question has: number, text, type, marks, and
  options for MCQ). Question numbers are global across all sections."
license: Proprietary
---

# Graded Assessment Document Skill

Generates a university-branded Graded Assessment `.docx` file by merging structured
assessment data into a `docxtpl` Word template.

## Template lookup

Templates are stored at:
```
assets/templates/{university_id}-assessment.docx
```

A reference template is available at:
```
assets/templates/reference-assessment-template.docx
```

## Input shape

```json
{
  "university_id": "xyz-university",
  "cover": {
    "university_name": "University of XYZ",
    "department": "Dept of Computer Science",
    "course_name": "Data Science 101",
    "assessment_title": "Mid-Term Graded Assessment",
    "semester": "Jan 2026",
    "date": "15 April 2026"
  },
  "instructions": {
    "duration": "2 Hours",
    "total_marks": 100,
    "passing_marks": 40,
    "attempt_rules": ["All questions in Section A are compulsory.", "Attempt any 3 from Section B."],
    "general_notes": ["No calculators allowed.", "Write clearly in blue or black ink."]
  },
  "sections": [
    {
      "letter": "A",
      "type_name": "Multiple Choice Questions",
      "total_marks": 20,
      "questions": [
        {
          "number": 1,
          "text": "What is Python?",
          "type": "mcq",
          "marks": 2,
          "options": { "a": "A snake", "b": "A programming language", "c": "A database", "d": "An OS" }
        }
      ]
    }
  ]
}
```

## Question types

| type | options required | rendered as |
|---|---|---|
| `mcq` | yes | Question + A/B/C/D vertical list |
| `short_answer` | no | Question text only |
| `long_answer` | no | Question text only |
| `fill_in_the_blank` | no | Sentence with `____________` inline blank |

## Output

Returns `GradedAssessmentResult` with:
- `output_path`: absolute path to the generated `.docx` file
- `university_id`: echoed back for traceability

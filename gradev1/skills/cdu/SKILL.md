---
name: cdu-assessment-doc
description: "Use this skill whenever a Graded Assessment Word document needs to
  be generated in CDU (Chaitanya Deemed University) format. Trigger when the user
  mentions Chaitanya university, CDU, or requests a multi-set question paper with
  Set A, Set B, and Set C variants — each containing Section A (10 short questions,
  answer any 6) and Section B (4 long-answer questions with OR alternates, answer
  any 2). CDU papers use a 2-column table layout with no CO or BTL columns. Do NOT
  trigger for other university formats."
license: Proprietary. LICENSE.txt has complete terms.
---

# CDU Graded Assessment Skill

Generates a `.docx` Graded Assessment document in Chaitanya Deemed University format —
a multi-set paper (Set A / Set B / Set C) where each set uses a 2-column table
(Q.No | Question) with Section A and Section B, and no CO or BTL columns.

---

## Core Workflow

1. **Collect inputs** — gather university name, course info, time, max marks, and
   all 3 sets. Each set needs: a label (Set-A / Set-B / Set-C), 10 Section A
   questions, and Section B question pairs (with OR).

2. **Validate question structure** — each set must have exactly 10 Section A
   questions and pairs in Section B. Section B instruction is fixed as
   "Answer the following Questions." Section A instruction is "Answer any six Questions."

3. **Generate the document** — call `CduAssessmentRequest` → `GradedAssessmentService().generate()`.
   The renderer builds one 2-column table per set, separated by page breaks:
   set header → time/marks row → Section A → Section B with OR rows.

4. **Verify output** — open or render the `.docx` to confirm:
   - Each set starts on a new page
   - Set header (label + university name) spans both columns and is centred/bold
   - Time and Max Marks appear in separate left/right cells on the same row
   - "Section - A" and "Section - B" labels span both columns and are bold
   - "(OR)" rows span both columns and are centred between question pairs
   - All 3 sets present (Set-A, Set-B, Set-C)

5. **Return the result** — provide the output file path from `GradedAssessmentResult.output_path`.

---

## Document Layout (per set)

```
┌──────────────────────────────────────────────────────────────┐
│           Set - A                                            │
│      CHAITANYA (DEEMED TO BE UNIVERSITY)                     │
│       B.Tech – CSE – English                                 │
├─────────────────────────────────┬────────────────────────────┤
│ Time: 1½ Hrs]                   │       [Max. Marks: 50      │
├──────────────────────────────────────────────────────────────┤
│                    Section - A                               │
├──────────────────────────────────────────────────────────────┤
│             Answer any six Questions.                        │
├──────────┬───────────────────────────────────────────────────┤
│ 1.       │ The sentences given below are in a jumbled order …│
│ 2.       │ Write one sentence using future perfect tense …   │
│ 3.       │ Rearrange the following jumbled words …           │
│ …        │ …  (10 questions total)                           │
├──────────────────────────────────────────────────────────────┤
│                    Section - B                               │
├──────────────────────────────────────────────────────────────┤
│              Answer the following Questions.                 │
├──────────┬───────────────────────────────────────────────────┤
│ 11       │ Write a report for a history journal …            │
├──────────────────────────────────────────────────────────────┤
│                          OR                                  │
├──────────┬───────────────────────────────────────────────────┤
│ 12       │ Write a Question-Answer dialogue …                │
│ 13       │ Write a short historical report …                 │
├──────────────────────────────────────────────────────────────┤
│                          OR                                  │
├──────────┬───────────────────────────────────────────────────┤
│ 14       │ Write a Question-Answer dialogue …                │
└──────────┴───────────────────────────────────────────────────┘
```

Three identical-structure tables follow (Set-A, Set-B, Set-C), each on its own page,
with different question content.

---

## Input Shape

```python
CduAssessmentRequest(
    university_id   = "cdu",          # fixed — selects CDU renderer
    university_name = "CHAITANYA (DEEMED TO BE UNIVERSITY)",
    course_info     = "B.Tech – CSE – English",
    time            = "1½ Hrs",
    max_marks       = 50,
    sets = [
        CduSet(
            label = "Set - A",
            section_a = CduSectionA(
                instruction = "Answer any six Questions.",
                questions   = [
                    CduQuestion(number="1.",  text="The sentences given below are in a jumbled order …"),
                    CduQuestion(number="2.",  text="Write one sentence using future perfect tense …"),
                    CduQuestion(number="3.",  text="Rearrange the following jumbled words …"),
                    CduQuestion(number="4.",  text="Choose the correct option from the brackets …"),
                    CduQuestion(number="5.",  text="Each of the following sentences contains an error …"),
                    CduQuestion(number="6.",  text="Fill in the blank with the most appropriate …"),
                    CduQuestion(number="7.",  text="Fill in the blank with the most appropriate …"),
                    CduQuestion(number="8.",  text="Rewrite the sentence using future perfect …"),
                    CduQuestion(number="9.",  text="Choose the correct option to complete …"),
                    CduQuestion(number="10.", text="Choose the correct option from the brackets …"),
                ],
            ),
            section_b = CduSectionB(
                instruction     = "Answer the following Questions.",
                question_pairs  = [
                    CduQuestionPair(
                        a = CduQuestion(number="11", text="Write a report for a history journal …"),
                        b = CduQuestion(number="12", text="Write a Question-Answer dialogue …"),
                    ),
                    CduQuestionPair(
                        a = CduQuestion(number="13", text="Write a short historical report …"),
                        b = CduQuestion(number="14", text="Write a Question-Answer dialogue …"),
                    ),
                ],
            ),
        ),
        # Set-B and Set-C follow the same structure with different questions
    ],
)
```

---

## Output

- File saved to: `artifacts/graded-assessments/cdu-assessment-{uid}.docx`
- Returns: `GradedAssessmentResult(output_path=..., university_id="cdu")`
- Open in Microsoft Word or LibreOffice to review before sharing

---

## Validation Checklist

- [ ] Document contains exactly 3 sets (Set-A, Set-B, Set-C)
- [ ] Each set starts on its own page
- [ ] Set header spans both columns and is centred and bold
- [ ] Time appears left-aligned; Max Marks appears right-aligned in the same row
- [ ] "Section - A" and "Section - B" labels span both columns
- [ ] Each set has exactly 10 Section A questions
- [ ] Section B OR rows span both columns and are centred
- [ ] No CO or BTL columns present anywhere in the document

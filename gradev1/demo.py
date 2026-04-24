import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "libs" / "src"))

from graded_assessment.application.generation_service import GradedAssessmentService
from graded_assessment.domain.amet_types import (
    AmetAssessmentRequest, AmetPartA, AmetPartB, AmetPartC,
    AmetQuestion, AmetQuestionPair,
)
from graded_assessment.domain.anu_types import (
    AnuAssessmentRequest, AnuPartA, AnuPartB,
    AnuSubQuestion, AnuPartBQuestion,
)
from graded_assessment.domain.cdu_types import (
    CduAssessmentRequest, CduSet, CduSectionA, CduSectionB,
    CduQuestion, CduQuestionPair,
)
from graded_assessment.domain.svyasa_types import (
    SvyasaAssessmentRequest, SvyasaPartA, SvyasaPartB,
    SvyasaQuestion, SvyasaQuestionPair,
)

svc = GradedAssessmentService()
generated = []

# ─────────────────────────────────────────────────────────────
# AMET
# ─────────────────────────────────────────────────────────────
amet_req = AmetAssessmentRequest(
    exam_type="MODEL EXAMINATIONS – APRIL 2026",
    programme="B.Tech SE/CSE",
    semester="II",
    course_name="Communicative English Advanced",
    course_code="256EN1A22TD",
    duration="3 hours",
    max_marks=100,
    instructions=[
        "Before attempting any question paper, ensure that you have received the correct question paper.",
        "The missing data, if any, may be assumed suitably.",
        "Use sketches wherever necessary.",
        "Use of dictionary / data book is NOT permitted.",
    ],
    part_a=AmetPartA(
        total="20×1 = 20 Marks",
        instruction="Answer all the questions",
        questions=[
            AmetQuestion(number="1",  text="Choose the correct option that completes the sentence: She ______ to the market every day.", mark=1, btl="K2", co="CO1"),
            AmetQuestion(number="2",  text="Identify the word most similar in meaning to 'Eloquent'.", mark=1, btl="K2", co="CO1"),
            AmetQuestion(number="3",  text="Choose the option that best completes the blank: He is neither honest ______ hardworking.", mark=1, btl="K2", co="CO2"),
            AmetQuestion(number="4",  text="Identify the word opposite in meaning to 'Benevolent'.", mark=1, btl="K2", co="CO2"),
            AmetQuestion(number="5",  text="Identify the word opposite in meaning to 'Verbose'.", mark=1, btl="K2", co="CO2"),
            AmetQuestion(number="6",  text="Complete the pair with the same logical relation: Light : Dark :: Joy : ______", mark=1, btl="K2", co="CO3"),
            AmetQuestion(number="7",  text="Identify the word opposite in meaning to 'Diligent'.", mark=1, btl="K2", co="CO3"),
            AmetQuestion(number="8",  text="Choose the correct option that completes the sentence: The committee ______ its decision yesterday.", mark=1, btl="K2", co="CO3"),
            AmetQuestion(number="9",  text="Identify the word opposite in meaning to 'Transparent'.", mark=1, btl="K2", co="CO4"),
            AmetQuestion(number="10", text="Complete the analogy: Diplomatic : Tact :: Courageous : ______", mark=1, btl="K2", co="CO4"),
            AmetQuestion(number="11", text="Identify the word most similar in meaning to 'Ambiguous'.", mark=1, btl="K2", co="CO4"),
            AmetQuestion(number="12", text="Arrange the following sentences in a logical order to form a coherent paragraph.", mark=1, btl="K2", co="CO4"),
            AmetQuestion(number="13", text="Choose the correct option that completes the sentence: The team ______ working on the project since morning.", mark=1, btl="K2", co="CO5"),
            AmetQuestion(number="14", text="Identify the word most similar in meaning to 'Pragmatic'.", mark=1, btl="K2", co="CO5"),
            AmetQuestion(number="15", text="Choose the correctly rearranged sentence from the options given below.", mark=1, btl="K2", co="CO5"),
            AmetQuestion(number="16", text="After reviewing the feedback from external evaluators, the board ______ its curriculum.", mark=1, btl="K3", co="CO5"),
            AmetQuestion(number="17", text="Choose the correct past perfect form of the verb in the sentence.", mark=1, btl="K3", co="CO5"),
            AmetQuestion(number="18", text="Identify the word opposite in meaning to 'Candid'.", mark=1, btl="K2", co="CO1"),
            AmetQuestion(number="19", text="Choose the correct form of sentence from the given alternatives.", mark=1, btl="K4", co="CO1"),
            AmetQuestion(number="20", text="Identify the word most similar in meaning to 'Meticulous'.", mark=1, btl="K2", co="CO2"),
        ],
    ),
    part_b=AmetPartB(
        total="5×14 = 70 Marks",
        instruction="Answer all the questions",
        question_pairs=[
            AmetQuestionPair(
                a=AmetQuestion(number="21 (a)", text="Write a paragraph of 200 words on the given topic: 'The role of communication in professional success'.", mark=14, btl="K6", co="CO1"),
                b=AmetQuestion(number="21 (b)", text="Write a paragraph of 200 words describing the importance of teamwork in an engineering environment.", mark=14, btl="K6", co="CO1"),
            ),
            AmetQuestionPair(
                a=AmetQuestion(number="22 (a)", text="Write a paragraph of about 150–180 words on the topic: 'Advantages of digital communication in maritime industry'.", mark=14, btl="K6", co="CO2"),
                b=AmetQuestion(number="22 (b)", text="Write a paragraph of about 170–200 words on the topic: 'Safety protocols in modern shipping'.", mark=14, btl="K6", co="CO2"),
            ),
            AmetQuestionPair(
                a=AmetQuestion(number="23 (a)", text="Two colleagues, Ravi and Priya, are discussing a project deadline. Write a dialogue of about 200 words between them.", mark=14, btl="K6", co="CO3"),
                b=AmetQuestion(number="23 (b)", text="You are a marine engineer. Describe in 200 words the environmental impact of oil spills and measures to prevent them.", mark=14, btl="K6", co="CO3"),
            ),
            AmetQuestionPair(
                a=AmetQuestion(number="24 (a)", text="Write a paragraph of about 170–200 words on the topic: 'Leadership qualities required for a ship's captain'.", mark=14, btl="K6", co="CO4"),
                b=AmetQuestion(number="24 (b)", text="Write a Question-Answer dialogue of about 200 words between an interviewer and a fresh marine engineering graduate.", mark=14, btl="K6", co="CO4"),
            ),
            AmetQuestionPair(
                a=AmetQuestion(number="25 (a)", text="Write a detailed paragraph in about 170–200 words on the topic: 'Future of autonomous ships in global trade'.", mark=14, btl="K6", co="CO5"),
                b=AmetQuestion(number="25 (b)", text="Write a story in about 170–200 words that illustrates effective crisis communication on board a vessel.", mark=14, btl="K6", co="CO5"),
            ),
        ],
    ),
    part_c=AmetPartC(
        total="1×10 = 10 Marks",
        instruction="Answer the Question",
        question=AmetQuestion(
            number="26",
            text="Read the following case study and answer the questions that follow:\n\n"
                 "Captain Arjun is the master of a cargo vessel carrying hazardous chemicals. "
                 "During a voyage, a minor fire breaks out in the engine room. The crew panics "
                 "and communication breaks down. Arjun must act decisively.\n\n"
                 "(a) What communication strategies should Arjun employ? (4 marks)\n"
                 "(b) How should the incident be documented and reported? (3 marks)\n"
                 "(c) What lessons can be drawn for future crisis management? (3 marks)",
            mark=10, btl="K3-K5", co="CO5",
        ),
    ),
)

r = svc.generate(amet_req)
generated.append(("AMET", r.output_path))

# ─────────────────────────────────────────────────────────────
# ANU
# ─────────────────────────────────────────────────────────────
anu_req = AnuAssessmentRequest(
    university_name="ANNAMACHARYA UNIVERSITY",
    batch="II B.Tech I Semester – CSE & Allied Branches",
    exam_type="IInd Mid Examination",
    course_name="Professional Skills for Engineers",
    date="28-08-2025",
    duration="2Hrs",
    max_marks=30,
    notes=[
        "Question Paper consists of two parts (Part-A and Part-B)",
        "In Part-A, each question carries one mark.",
        "30 marks in Part-B will be condensed to 25 marks.",
        "Answer ALL the questions in Part-A and Part-B",
    ],
    part_a=AnuPartA(
        sub_questions=[
            AnuSubQuestion(sub="a)", text="Fill in the blanks using the correct form of the verb: She ______ (write) her report when the power went out.", co="CO1", bloom="L1"),
            AnuSubQuestion(sub="b)", text="Identify and correct the error in the sentence: 'Each of the students have submitted their assignments.'", co="CO1", bloom="L2"),
            AnuSubQuestion(sub="c)", text="Choose the option which replaces the word 'Meticulous' correctly: (i) Careless  (ii) Thorough  (iii) Hasty  (iv) Vague", co="CO1", bloom="L2"),
            AnuSubQuestion(sub="d)", text="Rearrange the jumbled words to form one meaningful sentence: quickly / the / engineer / problem / solved / the", co="CO1", bloom="L2"),
            AnuSubQuestion(sub="e)", text="Convert the sentence from active voice to passive voice: 'The manager reviewed all the reports last night.'", co="CO1", bloom="L1"),
        ],
    ),
    part_b=AnuPartB(
        questions=[
            AnuPartBQuestion(number="2",    text="Read the passage and answer the following questions:\n\nArtificial Intelligence is transforming industries at an unprecedented pace. Engineers today must not only master technical skills but also develop strong communication and problem-solving abilities to work alongside AI systems effectively.", marks="",    co="",    bloom=""),
            AnuPartBQuestion(number="",     text="What is the central idea of the passage?",                                    marks="2M",  co="CO4", bloom="L1"),
            AnuPartBQuestion(number="",     text="Why must engineers develop communication skills according to the passage?",    marks="2M",  co="CO4", bloom="L2"),
            AnuPartBQuestion(number="",     text="How is AI transforming engineering roles?",                                   marks="2M",  co="CO4", bloom="L3"),
            AnuPartBQuestion(number="",     text="Analyse the impact of AI on traditional engineering practices.",              marks="2M",  co="CO4", bloom="L3"),
            AnuPartBQuestion(number="",     text="Discuss whether engineers should fear or embrace AI transformation.",         marks="2M",  co="CO4", bloom="L4"),
            AnuPartBQuestion(number="(OR)", text="(OR)",                                                                        marks="",    co="",    bloom=""),
            AnuPartBQuestion(number="3",    text="Rearrange the following sentences to show the correct sequence of steps for writing a technical report.", marks="10M", co="CO1", bloom="L2"),
            AnuPartBQuestion(number="4",    text="Write a paragraph on the topic: 'The Importance of Soft Skills in Engineering Careers' (200–250 words).", marks="10M", co="CO2", bloom="L4"),
            AnuPartBQuestion(number="(OR)", text="(OR)",                                                                        marks="",    co="",    bloom=""),
            AnuPartBQuestion(number="5",    text="Write a paragraph in 200–250 words about the role of teamwork in successful project delivery.", marks="10M", co="CO2", bloom="L4"),
            AnuPartBQuestion(number="6",    text="The following passage is in simple present tense. Rewrite it in simple past tense making all necessary changes.", marks="10M", co="CO2", bloom="L2"),
            AnuPartBQuestion(number="(OR)", text="(OR)",                                                                        marks="",    co="",    bloom=""),
            AnuPartBQuestion(number="7",    text="The following passage is in simple past tense. Rewrite it in present perfect tense with all necessary changes.", marks="10M", co="CO2", bloom="L2"),
        ],
    ),
)

r = svc.generate(anu_req)
generated.append(("ANU", r.output_path))

# ─────────────────────────────────────────────────────────────
# CDU
# ─────────────────────────────────────────────────────────────
cdu_req = CduAssessmentRequest(
    university_name="CHAITANYA (DEEMED TO BE UNIVERSITY)",
    course_info="B.Tech – CSE – Professional English",
    time="1½ Hrs",
    max_marks=50,
    sets=[
        CduSet(
            label="Set - A",
            section_a=CduSectionA(
                instruction="Answer any six Questions.",
                questions=[
                    CduQuestion(number="1.",  text="The sentences given below are in a jumbled order. Rearrange them to form a coherent paragraph."),
                    CduQuestion(number="2.",  text="Write one sentence using future perfect tense with the word 'complete'."),
                    CduQuestion(number="3.",  text="Rearrange the following jumbled words to form a meaningful sentence: always / a / positive / maintain / attitude / you / should"),
                    CduQuestion(number="4.",  text="Choose the correct option from the brackets to complete the sentence: The project (was completed / were completed) on time."),
                    CduQuestion(number="5.",  text="Each of the following sentences contains an error. Identify and correct it: 'The datas were collected from various sources.'"),
                    CduQuestion(number="6.",  text="Fill in the blank with the most appropriate word: Effective communication is the ______ of a successful team."),
                    CduQuestion(number="7.",  text="Fill in the blank with the most appropriate preposition: She has been working on this project ______ three months."),
                    CduQuestion(number="8.",  text="Rewrite the sentence using future perfect tense: 'She submits the report by tomorrow.'"),
                    CduQuestion(number="9.",  text="Choose the correct option to complete the sentence: Neither the manager nor the employees ______ aware of the change."),
                    CduQuestion(number="10.", text="Choose the correct option from the brackets: He is (good / well) at solving complex engineering problems."),
                ],
            ),
            section_b=CduSectionB(
                instruction="Answer the following Questions.",
                question_pairs=[
                    CduQuestionPair(
                        a=CduQuestion(number="11", text="Write a report for a college magazine about the annual technical fest held at your institution. (170–200 words)"),
                        b=CduQuestion(number="12", text="Write a Question-Answer dialogue of about 200 words between a student and a professor discussing career options after B.Tech."),
                    ),
                    CduQuestionPair(
                        a=CduQuestion(number="13", text="Write a short report on the impact of social media on student productivity. (170–200 words)"),
                        b=CduQuestion(number="14", text="Write a Question-Answer dialogue of about 200 words between two engineers discussing the pros and cons of remote working."),
                    ),
                ],
            ),
        ),
        CduSet(
            label="Set - B",
            section_a=CduSectionA(
                instruction="Answer any six Questions.",
                questions=[
                    CduQuestion(number="1.",  text="Choose the correct option to complete the sentence: If I ______ (know) the answer, I would have told you."),
                    CduQuestion(number="2.",  text="Write one sentence using future perfect tense with the word 'finish'."),
                    CduQuestion(number="3.",  text="Each of the following sentences contains an error. Identify and correct it: 'He don't know how to use the equipment.'"),
                    CduQuestion(number="4.",  text="Fill in the blank with the most appropriate word: The engineer's ______ to detail ensured a flawless design."),
                    CduQuestion(number="5.",  text="The sentences given below are in a jumbled order. Rearrange them to form a coherent paragraph."),
                    CduQuestion(number="6.",  text="Choose the correct option to complete the sentence: The committee (has / have) submitted its final report."),
                    CduQuestion(number="7.",  text="Fill in the blank with the most appropriate preposition: The seminar starts ______ 9 AM sharp."),
                    CduQuestion(number="8.",  text="Rearrange the jumbled words to form a coherent sentence: meeting / postponed / the / has / been / tomorrow's"),
                    CduQuestion(number="9.",  text="Choose the correct option from the brackets: She works (efficient / efficiently) under pressure."),
                    CduQuestion(number="10.", text="Each of the following sentences contains an error. Identify and correct it: 'The news are very surprising today.'"),
                ],
            ),
            section_b=CduSectionB(
                instruction="Answer the following Questions.",
                question_pairs=[
                    CduQuestionPair(
                        a=CduQuestion(number="11.", text="Write a paragraph of about 170–200 words on the topic: 'The role of engineers in sustainable development'."),
                        b=CduQuestion(number="12.", text="Write a short report for a school magazine on why coding should be introduced from primary school level."),
                    ),
                    CduQuestionPair(
                        a=CduQuestion(number="13.", text="You are a fresh engineering graduate. Describe in 200 words your experience during your first week at a tech company."),
                        b=CduQuestion(number="14.", text="Write a Question-Answer dialogue of about 200 words between a job interviewer and a candidate applying for a software role."),
                    ),
                ],
            ),
        ),
        CduSet(
            label="Set - C",
            section_a=CduSectionA(
                instruction="Answer any six Questions.",
                questions=[
                    CduQuestion(number="1.",  text="Each of the following sentences contains an error. Identify and correct it: 'The informations provided were incorrect.'"),
                    CduQuestion(number="2.",  text="Fill in the blank with the most appropriate word: Punctuality is a sign of ______ professionalism."),
                    CduQuestion(number="3.",  text="Choose the correct option to complete the sentence: By the time she arrives, we ______ (finish) the presentation."),
                    CduQuestion(number="4.",  text="Write one sentence using future perfect tense with the word 'deliver'."),
                    CduQuestion(number="5.",  text="Choose the correct verb form to complete the sentence: Every student ______ (is/are) expected to submit the assignment."),
                    CduQuestion(number="6.",  text="Fill in the blank with the most appropriate preposition: The report must be submitted ______ Friday."),
                    CduQuestion(number="7.",  text="Rearrange the jumbled words to form a coherent sentence: skills / communication / crucial / for / engineers / are"),
                    CduQuestion(number="8.",  text="Fill in the blank with the most appropriate word: The CEO's ______ speech motivated all the employees."),
                    CduQuestion(number="9.",  text="Rearrange the following jumbled words to form a meaningful sentence: deadline / the / team / met / successfully / project / the"),
                    CduQuestion(number="10.", text="Choose the correct option to complete the sentence: Neither the lecturer nor the students ______ prepared for the surprise test."),
                ],
            ),
            section_b=CduSectionB(
                instruction="Answer the following Questions.",
                question_pairs=[
                    CduQuestionPair(
                        a=CduQuestion(number="11.", text="Write a paragraph of about 170–200 words on the topic: 'How technology is reshaping modern workplaces'."),
                        b=CduQuestion(number="12.", text="Write a story about a young engineer who solves a critical problem under time pressure. (170–200 words)"),
                    ),
                    CduQuestionPair(
                        a=CduQuestion(number="13.", text="Write a paragraph of about 170–200 words discussing the advantages and disadvantages of online learning."),
                        b=CduQuestion(number="14.", text="Write a paragraph of about 170–200 words on the topic: 'The importance of ethics in engineering practice'."),
                    ),
                ],
            ),
        ),
    ],
)

r = svc.generate(cdu_req)
generated.append(("CDU", r.output_path))

# ─────────────────────────────────────────────────────────────
# S-VYASA
# ─────────────────────────────────────────────────────────────
svyasa_req = SvyasaAssessmentRequest(
    month_year="July 2025",
    academic_year="2024-25",
    program="B. Tech",
    specialization="All",
    semester="1",
    date_of_exam="",
    course_code="ENGL105",
    course_name="English LSRW",
    part_a=SvyasaPartA(
        questions=[
            SvyasaQuestion(number="1.",  text="Choose the correct collective noun to complete the sentence: A ______ of lions was spotted near the river.", co="5", rbtl="1", marks=3),
            SvyasaQuestion(number="2.",  text="Write two sentences using the word 'impact' — one as a noun and one as a verb.", co="2", rbtl="2", marks=3),
            SvyasaQuestion(number="3.",  text="Fill in the blanks by converting the noun to its adjective form: (i) Courage → ______  (ii) Wisdom → ______", co="5", rbtl="2", marks=3),
            SvyasaQuestion(number="4.",  text="Identify the error and rewrite the sentence correctly: 'She don't understand the importance of good communication.'", co="5", rbtl="2", marks=3),
            SvyasaQuestion(number="5.",  text="Fill in the blanks with the correct helping verb: (i) She ______ completed the assignment. (ii) They ______ working since morning.", co="4", rbtl="1", marks=3),
            SvyasaQuestion(number="6.",  text="Choose the correct option to complete the sentence: The report ______ (has been / have been) submitted to the director.", co="5", rbtl="1", marks=3),
            SvyasaQuestion(number="7.",  text="Fill in the blanks with suitable conjunctions: (i) He is smart ______ hardworking. (ii) She was tired, ______ she completed the task.", co="5", rbtl="2", marks=3),
            SvyasaQuestion(number="8.",  text="Expand the contractions and rewrite the sentences: (i) I can't attend the meeting. (ii) She doesn't know the answer.", co="5", rbtl="2", marks=3),
            SvyasaQuestion(number="9.",  text="Fill in the blanks with the correct option: Listening is as important as ______ (speaking / to speak / spoke) in effective communication.", co="3", rbtl="1", marks=3),
            SvyasaQuestion(number="10.", text="Fill in the blanks with the correct option (preposition): The seminar on communication skills will be held ______ the main auditorium ______ Friday morning.", co="3", rbtl="1", marks=3),
        ],
    ),
    part_b=SvyasaPartB(
        question_pairs=[
            SvyasaQuestionPair(
                a=SvyasaQuestion(number="11a.", text="Read the following passage and answer the questions below:\n'Effective communication is the foundation of all human relationships. In professional settings, the ability to express ideas clearly and listen actively determines success. Engineers who communicate well tend to lead better teams and deliver superior results.'\n(i) What is the main idea of the passage? (ii) What qualities of an engineer are highlighted? (iii) Why is listening important in communication? (iv) Write a suitable title for the passage.", co="2", rbtl="4", marks=14),
                b=SvyasaQuestion(number="11b.", text="Read the following passage carefully and answer the questions that follow:\n'The rise of remote work has changed the dynamics of workplace communication. Teams spread across time zones rely on written communication, video calls, and collaborative tools. Clear and concise writing has become a critical skill for every professional.'\n(i) What has changed workplace communication? (ii) What tools do remote teams use? (iii) Which skill has become critical? (iv) Suggest a title for the passage.", co="5", rbtl="4", marks=14),
            ),
            SvyasaQuestionPair(
                a=SvyasaQuestion(number="12a.", text="Write a product description in 200–250 words for a new smart engineering toolkit designed for field engineers. Include features, benefits, and a call to action.", co="5", rbtl="4", marks=14),
                b=SvyasaQuestion(number="12b.", text="Write a well-organized paragraph of about 200–250 words on the topic: 'The role of English language skills in global engineering careers'.", co="5", rbtl="4", marks=14),
            ),
            SvyasaQuestionPair(
                a=SvyasaQuestion(number="13a.", text="Develop a story in about 150–180 words using the following cues: A young engineer — remote project site — unexpected technical failure — quick thinking — team saves the day.", co="4", rbtl="5", marks=14),
                b=SvyasaQuestion(number="13b.", text="Develop a story in about 150–180 words using the following cues: A fresh graduate — first job interview — nervousness — honest answers — unexpected result.", co="4", rbtl="5", marks=14),
            ),
            SvyasaQuestionPair(
                a=SvyasaQuestion(number="14a.", text="The steps below explain how to write a professional email. Rearrange them in the correct order and write a sample email based on the situation: Informing your manager about a project delay due to material shortage.", co="1", rbtl="3", marks=14),
                b=SvyasaQuestion(number="14b.", text="Write an interview in 7 questions and 7 answers between a journalist and a renowned environmental engineer about sustainable construction practices.", co="5", rbtl="3", marks=14),
            ),
            SvyasaQuestionPair(
                a=SvyasaQuestion(number="15a.", text="Write a paragraph based on the situation: You attended a national-level technical symposium. Describe your experience, what you learned, and how it will help your career. (170–200 words)", co="4", rbtl="4", marks=14),
                b=SvyasaQuestion(number="15b.", text="Read the paragraph carefully. Change it from simple present tense to simple past tense, making all necessary grammatical changes throughout the passage.", co="3", rbtl="3", marks=14),
            ),
        ],
    ),
)

r = svc.generate(svyasa_req)
generated.append(("S-Vyasa", r.output_path))

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  GENERATED DOCUMENTS")
print("=" * 60)
for university, path in generated:
    size = Path(path).stat().st_size
    print(f"  {university:<12} {Path(path).name}  ({size:,} bytes)")
print("=" * 60)
print(f"\nAll files saved in: d:\\gradev1\\artifacts\\graded-assessments\\")
print("Open each file in Microsoft Word to review the layout.")

"""
Creates a test Google Sheet for AMET with all required tabs and sample data,
then prints the spreadsheet ID to use with the pipeline.

Run:
    python scripts/create_test_sheet.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

GWS = r"C:\tools\gws.exe"


def gws(*args) -> dict:
    result = subprocess.run([GWS, *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"gws error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def create_spreadsheet(title: str) -> str:
    data = gws("sheets", "spreadsheets", "create",
               "--json", json.dumps({"properties": {"title": title}}))
    return data["spreadsheetId"]


def add_sheets(spreadsheet_id: str, titles: list[str]) -> None:
    requests = [{"addSheet": {"properties": {"title": t}}} for t in titles]
    gws("sheets", "spreadsheets", "batchUpdate",
        "--params", json.dumps({"spreadsheetId": spreadsheet_id}),
        "--json", json.dumps({"requests": requests}))


def rename_sheet(spreadsheet_id: str, old_title: str, new_title: str, sheet_id: int = 0) -> None:
    request = {"updateSheetProperties": {
        "properties": {"sheetId": sheet_id, "title": new_title},
        "fields": "title"
    }}
    gws("sheets", "spreadsheets", "batchUpdate",
        "--params", json.dumps({"spreadsheetId": spreadsheet_id}),
        "--json", json.dumps({"requests": [request]}))


def write_values(spreadsheet_id: str, ranges_data: list[dict]) -> None:
    body = {"valueInputOption": "RAW", "data": ranges_data}
    gws("sheets", "spreadsheets", "values", "batchUpdate",
        "--params", json.dumps({"spreadsheetId": spreadsheet_id}),
        "--json", json.dumps(body))


def main():
    print("Creating test spreadsheet...")
    sid = create_spreadsheet("AMET Graded Assessment — Test")
    print(f"Created: https://docs.google.com/spreadsheets/d/{sid}/edit")

    # Default sheet is Sheet1 — rename to Config
    rename_sheet(sid, "Sheet1", "Config", sheet_id=0)

    # Add remaining tabs
    print("Adding tabs: Instructions, Part_A, Part_B, Part_C ...")
    add_sheets(sid, ["Instructions", "Part_A", "Part_B", "Part_C"])

    # ── Populate Config ──────────────────────────────────────────
    print("Writing Config tab...")
    write_values(sid, [{
        "range": "Config!A1:B15",
        "values": [
            ["key",                "value"],
            ["exam_type",          "MODEL EXAMINATIONS – APRIL 2026"],
            ["programme",          "B.Tech SE/CSE"],
            ["semester",           "II"],
            ["course_name",        "Communicative English Advanced"],
            ["course_code",        "256EN1A22TD"],
            ["duration",           "3 hours"],
            ["max_marks",          "100"],
            ["part_a_total",       "20×1 = 20 Marks"],
            ["part_a_instruction", "Answer all the questions"],
            ["part_b_total",       "5×14 = 70 Marks"],
            ["part_b_instruction", "Answer all the questions"],
            ["part_c_total",       "1×10 = 10 Marks"],
            ["part_c_instruction", "Answer the Question"],
        ]
    }])

    # ── Populate Instructions ────────────────────────────────────
    print("Writing Instructions tab...")
    write_values(sid, [{
        "range": "Instructions!A1:A5",
        "values": [
            ["instruction"],
            ["Before attempting any question paper, ensure that you have received the correct question paper."],
            ["The missing data, if any, may be assumed suitably."],
            ["Use sketches wherever necessary."],
            ["Use of dictionary / data book is NOT permitted."],
        ]
    }])

    # ── Populate Part_A ──────────────────────────────────────────
    print("Writing Part_A tab (20 questions)...")
    part_a = [
        ["number", "text",                                                                                          "mark", "btl", "co"],
        ["1",  "Choose the correct option that completes the sentence: She ______ to the market every day.",        "1",    "K2",  "CO1"],
        ["2",  "Identify the word most similar in meaning to 'Eloquent'.",                                          "1",    "K2",  "CO1"],
        ["3",  "Choose the option that best completes the blank: He is neither honest ______ hardworking.",         "1",    "K2",  "CO2"],
        ["4",  "Identify the word opposite in meaning to 'Benevolent'.",                                            "1",    "K2",  "CO2"],
        ["5",  "Identify the word opposite in meaning to 'Verbose'.",                                               "1",    "K2",  "CO2"],
        ["6",  "Complete the pair: Light : Dark :: Joy : ______",                                                   "1",    "K2",  "CO3"],
        ["7",  "Identify the word opposite in meaning to 'Diligent'.",                                              "1",    "K2",  "CO3"],
        ["8",  "Choose the correct option: The committee ______ its decision yesterday.",                           "1",    "K2",  "CO3"],
        ["9",  "Identify the word opposite in meaning to 'Transparent'.",                                           "1",    "K2",  "CO4"],
        ["10", "Complete the analogy: Diplomatic : Tact :: Courageous : ______",                                    "1",    "K2",  "CO4"],
        ["11", "Identify the word most similar in meaning to 'Ambiguous'.",                                         "1",    "K2",  "CO4"],
        ["12", "Arrange the following sentences in a logical order to form a coherent paragraph.",                  "1",    "K2",  "CO4"],
        ["13", "Choose the correct option: The team ______ working on the project since morning.",                  "1",    "K2",  "CO5"],
        ["14", "Identify the word most similar in meaning to 'Pragmatic'.",                                         "1",    "K2",  "CO5"],
        ["15", "Choose the correctly rearranged sentence from the options given below.",                            "1",    "K2",  "CO5"],
        ["16", "After reviewing the feedback from external evaluators the board ______ its curriculum.",            "1",    "K3",  "CO5"],
        ["17", "Choose the correct past perfect form of the verb in the sentence.",                                 "1",    "K3",  "CO5"],
        ["18", "Identify the word opposite in meaning to 'Candid'.",                                               "1",    "K2",  "CO1"],
        ["19", "Choose the correct form of sentence from the given alternatives.",                                  "1",    "K4",  "CO1"],
        ["20", "Identify the word most similar in meaning to 'Meticulous'.",                                        "1",    "K2",  "CO2"],
    ]
    write_values(sid, [{"range": "Part_A!A1:E21", "values": part_a}])

    # ── Populate Part_B ──────────────────────────────────────────
    print("Writing Part_B tab (5 pairs)...")
    part_b = [
        ["pair", "option", "number",   "text",                                                                                                       "mark", "btl", "co"],
        ["1",    "a",      "21 (a)",   "Write a paragraph of 200 words on: 'The role of communication in professional success'.",                    "14",   "K6",  "CO1"],
        ["1",    "b",      "21 (b)",   "Write a paragraph of 200 words describing the importance of teamwork in engineering.",                        "14",   "K6",  "CO1"],
        ["2",    "a",      "22 (a)",   "Write a paragraph on: 'Advantages of digital communication in maritime industry'. (150-180 words)",          "14",   "K6",  "CO2"],
        ["2",    "b",      "22 (b)",   "Write a paragraph on: 'Safety protocols in modern shipping'. (170-200 words)",                               "14",   "K6",  "CO2"],
        ["3",    "a",      "23 (a)",   "Write a dialogue of about 200 words between two colleagues Ravi and Priya discussing a project deadline.",    "14",   "K6",  "CO3"],
        ["3",    "b",      "23 (b)",   "Describe in 200 words the environmental impact of oil spills and measures to prevent them.",                  "14",   "K6",  "CO3"],
        ["4",    "a",      "24 (a)",   "Write a paragraph on: 'Leadership qualities required for a ship captain'. (170-200 words)",                  "14",   "K6",  "CO4"],
        ["4",    "b",      "24 (b)",   "Write a Q&A dialogue of 200 words between an interviewer and a fresh marine engineering graduate.",           "14",   "K6",  "CO4"],
        ["5",    "a",      "25 (a)",   "Write a detailed paragraph on: 'Future of autonomous ships in global trade'. (170-200 words)",               "14",   "K6",  "CO5"],
        ["5",    "b",      "25 (b)",   "Write a story in 170-200 words illustrating effective crisis communication on board a vessel.",               "14",   "K6",  "CO5"],
    ]
    write_values(sid, [{"range": "Part_B!A1:G11", "values": part_b}])

    # ── Populate Part_C ──────────────────────────────────────────
    print("Writing Part_C tab (1 case study)...")
    part_c = [
        ["number", "text",                                                                                                                                                                                                                                         "mark", "btl",    "co"],
        ["26",     "Captain Arjun is the master of a cargo vessel carrying hazardous chemicals. During a voyage a minor fire breaks out in the engine room. (a) What communication strategies should Arjun employ? (4M) (b) How should the incident be documented? (3M) (c) What lessons can be drawn for future crisis management? (3M)",
                   "10",    "K3-K5",  "CO5"],
    ]
    write_values(sid, [{"range": "Part_C!A1:E2", "values": part_c}])

    print(f"\n{'='*60}")
    print(f"  TEST SPREADSHEET READY")
    print(f"{'='*60}")
    print(f"  ID   : {sid}")
    print(f"  URL  : https://docs.google.com/spreadsheets/d/{sid}/edit")
    print(f"{'='*60}")
    print(f"\nRun the pipeline:")
    print(f"  python pipeline.py --university amet --spreadsheet {sid}")
    print(f"\nOr use the shared generator:")
    print(f"  python .agents/skills/generate/generate.py --university amet --spreadsheet {sid}")


if __name__ == "__main__":
    main()

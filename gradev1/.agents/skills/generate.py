"""
Shared Graded Assessment Generator
────────────────────────────────────
Single script used by all university skills.
Reads question data from Google Sheets, generates a .docx, and
optionally uploads it to Google Drive.

Usage
─────
  # From Google Sheets → generate → upload to Drive
  python generate.py --university amet     --spreadsheet SHEET_ID
  python generate.py --university anu      --spreadsheet SHEET_ID --folder DRIVE_FOLDER_ID
  python generate.py --university cdu      --spreadsheet SHEET_ID
  python generate.py --university s-vyasa  --spreadsheet SHEET_ID --folder DRIVE_FOLDER_ID

  # Parse only — print the request object, skip generation
  python generate.py --university amet --spreadsheet SHEET_ID --dry-run

Supported universities
──────────────────────
  amet      AMET University       — Part A (20 MCQ) + Part B (5 OR pairs) + Part C (case study)
  anu       Annamacharya Univ.    — Part A (5 sub-questions) + Part B (long answer with OR)
  cdu       Chaitanya Deemed Univ — Set A / B / C each with Section A and Section B
  s-vyasa   S-VYASA University    — Part A (10 Q × 3M) + Part B (5 pairs × 14M)

Google Sheet tab layout
────────────────────────
AMET        Config | Instructions | Part_A | Part_B | Part_C
ANU         Config | Notes | Part_A | Part_B
CDU         Config | Set_A | Set_B | Set_C
S-VYASA     Config | Part_A | Part_B

Config tab always: key (col A) | value (col B)
See sheet_parsers.py for full column details per tab.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import json
import sys
from pathlib import Path

# ── resolve project root and lib path ────────────────────────────────────────
# This file lives at .agents/skills/generate.py
# parents[0] = .agents/skills/
# parents[1] = .agents/
# parents[2] = project root (gradev1/)
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "libs" / "src"))
sys.path.insert(0, str(ROOT))

from graded_assessment.application.generation_service import GradedAssessmentService
from integrations.gws_client import upload_to_drive
from integrations.sheet_parsers import parse


# ── main pipeline ─────────────────────────────────────────────────────────────

def run(university_id: str, spreadsheet_id: str, folder_id: str | None, dry_run: bool) -> None:
    print(f"\n[1/3] Reading {university_id.upper()} questions from Google Sheets...")
    request = parse(university_id, spreadsheet_id)
    print(f"      Parsed successfully.")

    if dry_run:
        print("\n[DRY RUN] Request:")
        print(request.model_dump_json(indent=2))
        print("\n[DRY RUN] Skipping generation and upload.")
        return

    print(f"\n[2/3] Generating .docx document...")
    result = GradedAssessmentService().generate(request)
    print(f"      Saved → {result.output_path}")

    print(f"\n[3/3] Uploading to Google Drive...")
    meta = upload_to_drive(result.output_path, folder_id=folder_id)
    file_id   = meta.get("id", "unknown")
    file_name = meta.get("name", Path(result.output_path).name)
    print(f"      File   → {file_name}")
    print(f"      Link   → https://drive.google.com/file/d/{file_id}/view")
    print(f"\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Graded Assessment .docx from Google Sheets.")
    parser.add_argument("--university",  required=True, choices=["amet", "anu", "cdu", "s-vyasa"])
    parser.add_argument("--spreadsheet", required=True, help="Google Sheets ID")
    parser.add_argument("--folder",      default=None,  help="Google Drive folder ID to upload into")
    parser.add_argument("--dry-run",     action="store_true", help="Parse only, skip generation and upload")
    args = parser.parse_args()

    try:
        run(args.university, args.spreadsheet, args.folder, args.dry_run)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

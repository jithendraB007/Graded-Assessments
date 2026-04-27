"""
Graded Assessment Pipeline
───────────────────────────
Reads question data from Google Sheets → generates .docx → uploads to Google Drive.

Usage
─────
  python pipeline.py --university amet     --spreadsheet SHEET_ID
  python pipeline.py --university anu      --spreadsheet SHEET_ID --folder DRIVE_FOLDER_ID
  python pipeline.py --university cdu      --spreadsheet SHEET_ID --folder DRIVE_FOLDER_ID
  python pipeline.py --university s-vyasa  --spreadsheet SHEET_ID

Arguments
─────────
  --university   One of: amet | anu | cdu | s-vyasa
  --spreadsheet  Google Sheets ID (from the URL: .../spreadsheets/d/SHEET_ID/...)
  --folder       (optional) Google Drive folder ID to upload into
  --dry-run      Read and parse the sheet, print the request, skip generation and upload

Required Google Sheet structure
────────────────────────────────
See integrations/sheet_parsers.py for the full tab layout per university.

Quick reference:
  AMET     → tabs: Config, Instructions, Part_A, Part_B, Part_C
  ANU      → tabs: Config, Notes, Part_A, Part_B
  CDU      → tabs: Config, Set_A, Set_B, Set_C
  S-VYASA  → tabs: Config, Part_A, Part_B

Config tab always has two columns: key | value
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "libs" / "src"))

from graded_assessment.application.generation_service import GradedAssessmentService
from integrations.gws_client import upload_to_drive
from integrations.sheet_parsers import parse


def run(university_id: str, spreadsheet_id: str, folder_id: str | None, dry_run: bool) -> None:
    # ── Step 1: Read from Google Sheets ──────────────────────────────────────
    print(f"\n[1/3] Reading {university_id.upper()} questions from Google Sheets...")
    request = parse(university_id, spreadsheet_id)
    print(f"      Done — request parsed successfully.")

    if dry_run:
        print("\n[DRY RUN] Request object:")
        print(request.model_dump_json(indent=2))
        print("\n[DRY RUN] Skipping generation and upload.")
        return

    # ── Step 2: Generate .docx ────────────────────────────────────────────────
    print(f"\n[2/3] Generating .docx document...")
    result = GradedAssessmentService().generate(request)
    print(f"      Saved → {result.output_path}")

    # ── Step 3: Upload to Google Drive ────────────────────────────────────────
    print(f"\n[3/3] Uploading to Google Drive...")
    file_meta = upload_to_drive(result.output_path, folder_id=folder_id)
    drive_id   = file_meta.get("id", "unknown")
    drive_name = file_meta.get("name", Path(result.output_path).name)
    drive_link = f"https://drive.google.com/file/d/{drive_id}/view"

    print(f"      Uploaded → {drive_name}")
    print(f"      Drive ID → {drive_id}")
    print(f"      Link     → {drive_link}")
    print(f"\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read questions from Google Sheets, generate .docx, upload to Drive."
    )
    parser.add_argument("--university",   required=True, choices=["amet", "anu", "cdu", "s-vyasa"])
    parser.add_argument("--spreadsheet",  required=True, help="Google Sheets ID")
    parser.add_argument("--folder",       default=None,  help="Google Drive folder ID (optional)")
    parser.add_argument("--dry-run",      action="store_true", help="Parse only, skip generation and upload")
    args = parser.parse_args()

    try:
        run(args.university, args.spreadsheet, args.folder, args.dry_run)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

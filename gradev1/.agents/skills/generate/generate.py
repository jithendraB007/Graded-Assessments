"""
Shared Graded Assessment Generator
────────────────────────────────────
Reads question data from Google Sheets OR a CSV file, generates a .docx,
and uploads it to the university's Google Drive folder.

Usage
─────
  # From Google Sheets
  python generate.py --university amet    --spreadsheet SHEET_ID
  python generate.py --university anu     --spreadsheet SHEET_ID
  python generate.py --university cdu     --spreadsheet SHEET_ID
  python generate.py --university s-vyasa --spreadsheet SHEET_ID

  # From a CSV file
  python generate.py --university amet    --csv questions.csv
  python generate.py --university s-vyasa --csv questions.csv

  # Override Drive folder (defaults to university's dedicated folder)
  python generate.py --university amet --spreadsheet SHEET_ID --folder DRIVE_FOLDER_ID

  # Dry run — print parsed request, skip generation and upload
  python generate.py --university amet --spreadsheet SHEET_ID --dry-run

CSV format (8 columns: section, f1-f7)
───────────────────────────────────────
  AMET rows:
    config,      {key},   {value}
    instruction, {text}
    part_a,      {number},{text},  {mark},{btl}, {co}
    part_b,      {pair},  {option},{number},{text},{mark},{btl},{co}
    part_c,      {number},{text},  {mark},{btl}, {co}

  ANU rows:
    config,  {key},   {value}
    note,    {text}
    part_a,  {sub},   {text},{co},{bloom}
    part_b,  {number},{text},{marks},{co},{bloom}   (use number=(OR) for OR rows)

  CDU rows:
    config,   {key},   {value}
    set_a_a,  {number},{text}             <- Set A, Section A question
    set_a_b,  {pair},  {number},{text}    <- Set A, Section B pair row
    set_b_a/set_b_b/set_c_a/set_c_b — same for Set B and Set C

  S-VYASA rows:
    config,  {key},   {value}
    part_a,  {number},{text},{co},{rbtl},{marks}
    part_b,  {pair},  {option},{number},{text},{co},{rbtl},{marks}

See integrations/csv_parsers.py for full details.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(ROOT / "libs" / "src"))
sys.path.insert(0, str(ROOT))

from graded_assessment.application.generation_service import GradedAssessmentService
from integrations.csv_parsers import parse_csv
from integrations.drive_folders import get_folder
from integrations.gws_client import upload_to_drive
from integrations.sheet_parsers import parse as parse_sheets


def run(
    university_id: str,
    spreadsheet_id: str | None,
    csv_path: str | None,
    folder_id: str | None,
    dry_run: bool,
) -> None:
    # ── Step 1: Parse input ───────────────────────────────────────────────────
    if csv_path:
        print(f"\n[1/3] Reading {university_id.upper()} questions from CSV: {csv_path}")
        request = parse_csv(university_id, csv_path)
    else:
        print(f"\n[1/3] Reading {university_id.upper()} questions from Google Sheets...")
        request = parse_sheets(university_id, spreadsheet_id)
    print(f"      Parsed successfully.")

    if dry_run:
        print("\n[DRY RUN] Request:")
        print(request.model_dump_json(indent=2))
        print("\n[DRY RUN] Skipping generation and upload.")
        return

    # ── Step 2: Generate .docx ────────────────────────────────────────────────
    print(f"\n[2/3] Generating .docx document...")
    result = GradedAssessmentService().generate(request)
    print(f"      Saved -> {result.output_path}")

    # ── Step 3: Upload to Drive (auto-route to university folder) ─────────────
    target_folder = folder_id or get_folder(university_id)
    print(f"\n[3/3] Uploading to Google Drive...")
    if target_folder:
        print(f"      Folder -> {university_id.upper()} university folder")
    meta = upload_to_drive(result.output_path, folder_id=target_folder)
    file_id   = meta.get("id", "unknown")
    file_name = meta.get("name", Path(result.output_path).name)
    print(f"      File   -> {file_name}")
    print(f"      Link   -> https://drive.google.com/file/d/{file_id}/view")
    print(f"\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Graded Assessment .docx from Google Sheets or a CSV file."
    )
    parser.add_argument("--university",  required=True, choices=["amet", "anu", "cdu", "s-vyasa"])
    parser.add_argument("--spreadsheet", default=None, help="Google Sheets ID")
    parser.add_argument("--csv",         default=None, help="Path to question CSV file")
    parser.add_argument("--folder",      default=None, help="Drive folder ID (overrides university default)")
    parser.add_argument("--dry-run",     action="store_true", help="Parse only, skip generation and upload")
    args = parser.parse_args()

    if not args.spreadsheet and not args.csv:
        parser.error("Provide either --spreadsheet SHEET_ID or --csv FILE_PATH")

    try:
        run(args.university, args.spreadsheet, args.csv, args.folder, args.dry_run)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

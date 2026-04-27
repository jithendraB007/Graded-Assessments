"""Thin wrapper around the gws CLI for Sheets reads and Drive uploads."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _gws() -> str:
    found = shutil.which("gws")
    if found:
        return found
    fallback = Path(r"C:\tools\gws.exe")
    if fallback.exists():
        return str(fallback)
    raise RuntimeError(
        "gws not found. Install from https://github.com/googleworkspace/cli"
    )


def read_sheet(spreadsheet_id: str, range_: str) -> list[list[str]]:
    """Read a tab/range from Google Sheets. Returns rows as list of lists.
    Row 0 is always the header row."""
    result = subprocess.run(
        [_gws(), "sheets", "+read",
         "--spreadsheet", spreadsheet_id,
         "--range", range_],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gws sheets +read failed:\n{result.stderr}")
    data = json.loads(result.stdout)
    return data.get("values", [])


def upload_to_drive(file_path: str, folder_id: str | None = None, name: str | None = None) -> dict:
    """Upload a local file to Google Drive. Returns the Drive file metadata."""
    cmd = [_gws(), "drive", "+upload", file_path]
    if folder_id:
        cmd += ["--parent", folder_id]
    if name:
        cmd += ["--name", name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gws drive +upload failed:\n{result.stderr}")
    return json.loads(result.stdout)

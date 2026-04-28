"""
Maps each university_id to its dedicated Google Drive folder ID.
Pipeline uses this to auto-route uploads without needing --folder.
"""

UNIVERSITY_FOLDERS: dict[str, str] = {
    "amet":    "10IEEPoxcPcp6MTiELABUhTQGAxSIvVO7",
    "anu":     "12BjkhS1q-LUUbvQqJxsny1fPoqg8V-BH",
    "cdu":     "1-impXlcz2lolFqmdolKCYFXp9YaMp75y",
    "s-vyasa": "1uO99Psrf1RISL529TJWw9Z5ACoPcwysv",
}


def get_folder(university_id: str) -> str | None:
    """Return the Drive folder ID for the given university, or None if not configured."""
    return UNIVERSITY_FOLDERS.get(university_id)

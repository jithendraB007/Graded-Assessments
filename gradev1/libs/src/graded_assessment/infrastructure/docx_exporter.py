from __future__ import annotations

import uuid
from pathlib import Path

from graded_assessment.domain.types import GradedAssessmentResult

OUTPUT_DIR = Path(__file__).parents[4] / "artifacts" / "graded-assessments"


def export_to_file(docx_bytes: bytes, university_id: str) -> GradedAssessmentResult:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{university_id}-assessment-{uuid.uuid4().hex[:8]}.docx"
    output_path = OUTPUT_DIR / filename
    output_path.write_bytes(docx_bytes)
    return GradedAssessmentResult(output_path=str(output_path), university_id=university_id)

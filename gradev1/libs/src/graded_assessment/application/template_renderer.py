from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docxtpl import DocxTemplate

from graded_assessment.domain.types import GradedAssessmentRequest

TEMPLATE_DIR = Path(__file__).parents[4] / "assets" / "templates"


def render_to_bytes(request: GradedAssessmentRequest) -> bytes:
    template_path = TEMPLATE_DIR / f"{request.university_id}-assessment.docx"
    if not template_path.exists():
        raise FileNotFoundError(
            f"No Word template found for university '{request.university_id}'. "
            f"Expected: {template_path}"
        )

    doc = DocxTemplate(template_path)
    context = {
        "cover": request.cover.model_dump(),
        "instructions": request.instructions.model_dump(),
        "sections": [s.model_dump() for s in request.sections],
    }
    doc.render(context)

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()

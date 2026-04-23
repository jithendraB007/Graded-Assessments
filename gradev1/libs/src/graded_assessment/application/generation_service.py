from __future__ import annotations

from graded_assessment.application.renderers import amet_renderer, anu_renderer, cdu_renderer, svyasa_renderer
from graded_assessment.application.template_renderer import render_to_bytes
from graded_assessment.domain.amet_types import AmetAssessmentRequest
from graded_assessment.domain.anu_types import AnuAssessmentRequest
from graded_assessment.domain.cdu_types import CduAssessmentRequest
from graded_assessment.domain.svyasa_types import SvyasaAssessmentRequest
from graded_assessment.domain.types import GradedAssessmentRequest, GradedAssessmentResult
from graded_assessment.infrastructure.docx_exporter import export_to_file

_RENDERER_MAP = {
    "amet": amet_renderer.render,
    "anu": anu_renderer.render,
    "cdu": cdu_renderer.render,
    "s-vyasa": svyasa_renderer.render,
}

AssessmentRequest = (
    GradedAssessmentRequest
    | AmetAssessmentRequest
    | AnuAssessmentRequest
    | CduAssessmentRequest
    | SvyasaAssessmentRequest
)


class GradedAssessmentService:
    def generate(self, request: AssessmentRequest) -> GradedAssessmentResult:
        renderer = _RENDERER_MAP.get(request.university_id)
        if renderer:
            docx_bytes = renderer(request)
        else:
            docx_bytes = render_to_bytes(request)
        return export_to_file(docx_bytes, request.university_id)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "libs" / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from graded_assessment.application.generation_service import GradedAssessmentService
from graded_assessment.domain.types import GradedAssessmentRequest

app = FastAPI(title="Graded Assessment API")
service = GradedAssessmentService()


@app.post("/generate")
def generate(request: GradedAssessmentRequest):
    try:
        result = service.generate(request)
        return FileResponse(
            path=result.output_path,
            filename=Path(result.output_path).name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}

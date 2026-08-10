from fastapi import FastAPI, HTTPException

from app.models.chart import BirthInput, BirthChart
from app.services.chart_service import build_chart

app = FastAPI(
    title="Astro AI — Milestone 1",
    version="0.1.0",
    description="Vedic astrology birth-chart calculation API."
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "astro-ai-milestone1"}


@app.post("/api/v1/chart", response_model=BirthChart)
def create_chart(payload: BirthInput):
    try:
        return build_chart(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chart calculation failed: {exc}"
        ) from exc

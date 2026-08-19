from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8-sig")

if "marriage_synthesis_reasoning_v2" not in s:
    anchor = "from app.astrology.features.marriage_forecast_router_v3 import (\n    route_marriage_question_v3,\n)\n"
    insert = anchor + "\nfrom app.astrology.features.marriage_synthesis_reasoning_v2 import (\n    synthesize_marriage_profile_v2,\n)\n"
    if anchor not in s:
        raise RuntimeError("Marriage V3 import anchor not found")
    s = s.replace(anchor, insert, 1)

if "class MarriageSynthesisV2Request" not in s:
    anchor = "class CareerTransitRequest(BaseModel):\n"
    model = '''class MarriageSynthesisV2Request(BaseModel):\n    \"\"\"Full Marriage synthesis request.\"\"\"\n\n    birth: BirthInput\n    reference_moment: datetime\n    include_timing: bool = True\n\n\n'''
    if anchor not in s:
        raise RuntimeError("API request model anchor not found")
    s = s.replace(anchor, model + anchor, 1)

if '"/api/v1/marriage-synthesis-v2"' not in s:
    endpoint = '''\n\n# =========================================================\n# FULL MARRIAGE SYNTHESIS V2\n# =========================================================\n\n@app.post(\n    \"/api/v1/marriage-synthesis-v2\"\n)\ndef create_marriage_synthesis_v2(\n    payload: MarriageSynthesisV2Request,\n):\n    \"\"\"Build one coherent marriage profile from the existing V3 engines.\"\"\"\n    try:\n        chart = build_chart(payload.birth)\n        synthesis = synthesize_marriage_profile_v2(\n            chart,\n            payload.reference_moment,\n            include_timing=payload.include_timing,\n        )\n        return {\n            \"birth\": chart.get(\"birth\", {}),\n            \"synthesis\": synthesis,\n        }\n    except ValueError as exc:\n        raise HTTPException(status_code=400, detail=str(exc)) from exc\n    except Exception as exc:\n        raise HTTPException(\n            status_code=500,\n            detail=f\"Marriage synthesis generation failed: {exc}\",\n        ) from exc\n'''
    s = s.rstrip() + endpoint + "\n"

p.write_text(s, encoding="utf-8")

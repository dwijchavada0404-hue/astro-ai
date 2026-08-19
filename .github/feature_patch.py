from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"anchor not found: {label}")
    return text.replace(old, new, 1)


p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

s = replace_once(
    s,
    'from app.astrology.features.marriage_forecast_router_v3 import (\n    route_marriage_question_v3,\n)\n',
    'from app.astrology.features.marriage_forecast_router_v3 import (\n    route_marriage_question_v3,\n)\n\nfrom app.astrology.features.marriage_contextual_router_v1 import (\n    route_marriage_question_contextual_v1,\n)\n',
    "contextual router import",
)

s = replace_once(
    s,
    '    birth: BirthInput\n    question: str\n    reference_moment: datetime\n    previous_context: dict[str, Any] | None = None\n\n\nclass MarriageSynthesisV2Request',
    '    birth: BirthInput\n    question: str\n    reference_moment: datetime\n    previous_context: dict[str, Any] | None = None\n    relationship_status: str | None = None\n\n\nclass MarriageSynthesisV2Request',
    "MarriageQuestionV3Request relationship_status",
)

s = replace_once(
    s,
    '            route_marriage_question_v3(\n                chart,\n                question_analysis,\n                reference_moment,\n                previous_context=(\n                    payload.previous_context\n                ),\n            )',
    '            route_marriage_question_contextual_v1(\n                chart,\n                question_analysis,\n                reference_moment,\n                relationship_status=(\n                    payload.relationship_status\n                ),\n                previous_context=(\n                    payload.previous_context\n                ),\n            )',
    "Marriage V3 API contextual routing",
)

p.write_text(s, encoding="utf-8")

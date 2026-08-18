from datetime import datetime
import app.astrology.features.marriage_forecast_router_v3 as router
REF=datetime.fromisoformat("2026-08-15T12:00:00+05:30")
def test_router_dispatch(monkeypatch):
    expected={"available":True,"event":"spouse_education"}
    monkeypatch.setattr(router,"_route_spouse_education",lambda c,a,r:expected)
    qa={"primary_event":"spouse_education","query_mode":"single_event","intent":{}}
    assert router.route_marriage_question_v3({},qa,REF)==expected

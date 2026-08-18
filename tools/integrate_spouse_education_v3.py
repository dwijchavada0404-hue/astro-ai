from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
I=ROOT/'app/astrology/features/marriage_question_intelligence_v3.py'
R=ROOT/'app/astrology/features/marriage_forecast_router_v3.py'

def rep(t,a,b):
    if b in t:return t
    if a not in t:raise RuntimeError('anchor not found')
    return t.replace(a,b,1)

def patch_i():
    t=I.read_text(encoding='utf-8-sig')
    t=rep(t,'    "spouse_appearance": (\n        "Spouse Appearance / Physical Profile"\n    ),\n','    "spouse_appearance": (\n        "Spouse Appearance / Physical Profile"\n    ),\n    "spouse_education": (\n        "Spouse Education / Intellectual Profile"\n    ),\n')
    anchor='# =========================================================\n# SPOUSE APPEARANCE DETECTION\n# =========================================================\n'
    block=r'''# =========================================================
# SPOUSE EDUCATION DETECTION
# =========================================================

def _detect_spouse_education(question: str) -> dict[str, Any] | None:
    spouse_markers=("spouse","future spouse","partner","future partner","husband","wife","person i marry","person i will marry")
    if not any(x in question for x in spouse_markers): return None
    patterns=((r"\beducation\b","spouse education"),(r"\beducated\b","spouse educated"),(r"\bqualification\b","spouse qualification"),(r"\bqualified\b","spouse qualification"),(r"\bdegree\b","spouse degree"),(r"\bpostgraduate\b","spouse higher education"),(r"\bpost graduate\b","spouse higher education"),(r"\bmasters?\s+degree\b","spouse higher education"),(r"\bmaster's\s+degree\b","spouse higher education"),(r"\bdoctorate\b","spouse higher education"),(r"\bphd\b","spouse higher education"),(r"\bstudy\s+abroad\b","spouse international education"),(r"\bstudied\s+abroad\b","spouse international education"),(r"\beducated\s+abroad\b","spouse international education"),(r"\bforeign\s+university\b","spouse international education"),(r"\bstudy\s+law\b","spouse law education"),(r"\blaw\s+degree\b","spouse law education"),(r"\bstudy\s+design\b","spouse creative education"),(r"\bdesign\s+degree\b","spouse creative education"),(r"\bfinance\s+degree\b","spouse finance education"),(r"\bcommerce\s+(?:degree|background)\b","spouse commerce education"),(r"\bresearch\s+degree\b","spouse research education"),(r"\btechnical\s+(?:education|degree)\b","spouse technical education"),(r"\bcomputer\s+science\b","spouse technical education"),(r"\bprofessional\s+(?:qualification|degree)\b","spouse professional qualification"),(r"\bprofessionally\s+qualified\b","spouse professional qualification"),(r"\bchartered\s+accountant\b","spouse professional qualification"),(r"\bca\s+qualification\b","spouse professional qualification"),(r"\bmba\b","spouse professional qualification"),(r"\bintelligent\b","spouse intellect"),(r"\bintellectual\b","spouse intellect"),(r"\banalytical\b","spouse intellect"),(r"\bacademic[-\s]minded\b","spouse intellect"),(r"\blearning\s+style\b","spouse intellect"))
    matched=[]
    for pattern,label in patterns:
        if re.search(pattern,question) and label not in matched: matched.append(label)
    if not matched:return None
    return {"event":"spouse_education","event_label":EVENT_LABELS["spouse_education"],"matched_keywords":matched}


'''
    t=rep(t,anchor,block+anchor)
    a='''    # -----------------------------------------------------
    # SPOUSE APPEARANCE
    # -----------------------------------------------------

    spouse_appearance = (
        _detect_spouse_appearance(
            question
        )
    )
'''
    t=rep(t,a,'    # -----------------------------------------------------\n    # SPOUSE EDUCATION\n    # -----------------------------------------------------\n\n    spouse_education = _detect_spouse_education(question)\n    if spouse_education:\n        detected.append(spouse_education)\n\n'+a)
    a='''        if (
            "spouse_appearance"
            in special_names
            and event_name
            in (
                "spouse_traits",
                "marriage_timing",
                "general_marriage",
            )
        ):

            continue
'''
    t=rep(t,a,'        if (\n            "spouse_education" in special_names\n            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")\n        ):\n            continue\n\n'+a)
    a='''        if (
            "spouse_profession"
            in names
            and event_name
            in (
                "foreign_intercultural_connection",
                "spouse_appearance",
                "spouse_traits",
            )
        ):

            continue
'''
    t=rep(t,a,'        if (\n            "spouse_education" in names\n            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n        ):\n            continue\n\n'+a)
    t=rep(t,'        "spouse_appearance",\n        "spouse_profession",\n','        "spouse_appearance",\n        "spouse_education",\n        "spouse_profession",\n')
    t=rep(t,'        "spouse_meeting",\n        "spouse_profession",\n        "foreign_intercultural_connection",\n','        "spouse_meeting",\n        "spouse_education",\n        "spouse_profession",\n        "foreign_intercultural_connection",\n')
    t=rep(t,'        "spouse_profession",\n        "spouse_appearance",\n        "foreign_intercultural_connection",\n','        "spouse_profession",\n        "spouse_appearance",\n        "spouse_education",\n        "foreign_intercultural_connection",\n')
    t=rep(t,'        "spouse_appearance",\n        "spouse_profession",\n        "love_vs_arranged",\n','        "spouse_appearance",\n        "spouse_education",\n        "spouse_profession",\n        "love_vs_arranged",\n')
    t=rep(t,'        "spouse_traits",\n        "spouse_appearance",\n        "spouse_profession",\n        "foreign_intercultural_connection",\n','        "spouse_traits",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_profession",\n        "foreign_intercultural_connection",\n')
    I.write_text(t,encoding='utf-8')

def patch_r():
    t=R.read_text(encoding='utf-8-sig')
    t=rep(t,'from app.astrology.features.spouse_appearance_reasoning_v2 import (\n    analyze_spouse_appearance_v2,\n)\n','from app.astrology.features.spouse_appearance_reasoning_v2 import (\n    analyze_spouse_appearance_v2,\n)\n\nfrom app.astrology.features.spouse_education_reasoning_v2 import (\n    analyze_spouse_education_v2,\n)\n')
    t=rep(t,'    "spouse_appearance": (\n        "Spouse Appearance / Physical Profile"\n    ),\n','    "spouse_appearance": (\n        "Spouse Appearance / Physical Profile"\n    ),\n    "spouse_education": (\n        "Spouse Education / Intellectual Profile"\n    ),\n')
    anchor='# =========================================================\n# SPOUSE APPEARANCE ROUTE\n# =========================================================\n'
    route='''# =========================================================
# SPOUSE EDUCATION ROUTE
# =========================================================

def _route_spouse_education(chart: dict[str, Any], question_analysis: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    intent=_safe_dict(question_analysis.get("intent"))
    question=str(question_analysis.get("original_question",question_analysis.get("normalised_question","")) or "")
    analysis=analyze_spouse_education_v2(chart,question)
    result={"available":bool(analysis.get("available")),"route":"natal_evidence","event":"spouse_education","event_label":EVENT_LABELS["spouse_education"],"question_type":intent.get("question_type"),"direction":intent.get("direction"),"parser_confidence":intent.get("confidence"),"reference_moment":reference_moment.isoformat(),"evidence_engine":"spouse_education_reasoning_v2","forecast_type":"natal_pattern","model_version":analysis.get("model_version"),"question":analysis.get("question",question),"normalised_question":analysis.get("normalised_question",str(question_analysis.get("normalised_question","") or "")),"target":analysis.get("target"),"target_label":analysis.get("target_label"),"matched_keywords":analysis.get("matched_keywords",[]),"support_score":analysis.get("support_score"),"support_level":analysis.get("support_level"),"support_label":analysis.get("support_label"),"confidence":analysis.get("confidence"),"answer":analysis.get("answer"),"summary":analysis.get("summary"),"limitation":analysis.get("limitation"),"strongest_themes":analysis.get("strongest_themes",[]),"evidence_count":analysis.get("evidence_count",0),"evidence":analysis.get("evidence",[]),"natal_profile":analysis.get("natal_profile",{}),"natal_analysis":analysis.get("natal_analysis",{}),"analysis":analysis}
    if not analysis.get("available"): result["reason"]=analysis.get("reason")
    return result


'''
    t=rep(t,anchor,route+anchor)
    a='''    elif inherited_event == (
        "spouse_profession"
    ):
'''
    t=rep(t,a,'    elif inherited_event == (\n        "spouse_education"\n    ):\n\n        result = _route_spouse_education(chart, inherited_analysis, reference_moment)\n\n'+a)
    a='''    # -----------------------------------------------------
    # SPOUSE PROFESSION
    # -----------------------------------------------------

    if (
        query_mode
        == "single_event"
        and event_name
        == "spouse_profession"
    ):
'''
    t=rep(t,a,'    # -----------------------------------------------------\n    # SPOUSE EDUCATION\n    # -----------------------------------------------------\n\n    if query_mode == "single_event" and event_name == "spouse_education":\n        return _route_spouse_education(chart, question_analysis, reference_moment)\n\n'+a)
    R.write_text(t,encoding='utf-8')

def tests():
    (ROOT/'tests/test_spouse_education_intelligence_v3.py').write_text('''from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3\n\ndef test_spouse_education_detection():\n    for q in ["What kind of education will my future spouse have?","Will my spouse be highly educated?","Will my spouse have a finance degree?","Will my spouse be educated abroad?","Will my spouse be intelligent and analytical?"]:\n        r=analyze_marriage_question_v3(q)\n        assert r["primary_event"]=="spouse_education"\n        assert r["query_mode"]=="single_event"\n\ndef test_profession_not_hijacked():\n    assert analyze_marriage_question_v3("Will my spouse work in finance?")["primary_event"]=="spouse_profession"\n''',encoding='utf-8')
    (ROOT/'tests/test_spouse_education_router_v3.py').write_text('''from datetime import datetime\nimport app.astrology.features.marriage_forecast_router_v3 as router\nREF=datetime.fromisoformat("2026-08-15T12:00:00+05:30")\ndef test_router_dispatch(monkeypatch):\n    expected={"available":True,"event":"spouse_education"}\n    monkeypatch.setattr(router,"_route_spouse_education",lambda c,a,r:expected)\n    qa={"primary_event":"spouse_education","query_mode":"single_event","intent":{}}\n    assert router.route_marriage_question_v3({},qa,REF)==expected\n''',encoding='utf-8')
    (ROOT/'tests/test_spouse_education_api_v3.py').write_text('''from fastapi.testclient import TestClient\nfrom app.main import app\nfrom app.services import chart_service\nclient=TestClient(app)\ndef rp(place): return {"resolved_name":"Mumbai, Maharashtra, India","latitude":19.076,"longitude":72.8777,"timezone":"Asia/Kolkata"}\ndef payload(q): return {"birth":{"date":"2000-04-04","time":"14:04:00","place":"Mumbai, Maharashtra, India"},"question":q,"reference_moment":"2026-08-15T12:00:00+05:30"}\ndef test_api(monkeypatch):\n    monkeypatch.setattr(chart_service,"resolve_place",rp)\n    response=client.post("/api/v1/marriage-question-v3",json=payload("Will my spouse be highly educated?"))\n    assert response.status_code==200\n    body=response.json()\n    assert body["understanding"]["primary_event"]=="spouse_education"\n    assert body["result"]["event"]=="spouse_education"\n    assert body["result"]["evidence_engine"]=="spouse_education_reasoning_v2"\ndef test_finance_degree(monkeypatch):\n    monkeypatch.setattr(chart_service,"resolve_place",rp)\n    body=client.post("/api/v1/marriage-question-v3",json=payload("Will my spouse have a finance degree?")).json()\n    assert body["understanding"]["primary_event"]=="spouse_education"\n    assert body["result"]["target"]=="finance_commerce"\n''',encoding='utf-8')
patch_i();patch_r();tests()

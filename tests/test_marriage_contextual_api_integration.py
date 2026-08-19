import inspect

from app.main import MarriageQuestionV3Request, answer_marriage_question_v3, app


def test_marriage_v3_request_accepts_relationship_status():
    assert "relationship_status" in MarriageQuestionV3Request.model_fields
    assert MarriageQuestionV3Request.model_fields["relationship_status"].default is None


def test_marriage_v3_endpoint_uses_contextual_router():
    source = inspect.getsource(answer_marriage_question_v3)
    assert "route_marriage_question_contextual_v1" in source
    assert "payload.relationship_status" in source


def test_marriage_v3_route_remains_registered():
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/api/v1/marriage-question-v3" in paths

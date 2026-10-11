from fastapi.testclient import TestClient

from secure_triage_api import app

client = TestClient(app)


def operator_token() -> str:
    response = client.post("/token", json={"username": "operator", "password": "operator-pass"})
    return response.json()["access_token"]


def test_agent_requires_existing_jwt_authentication():
    response = client.post("/agent/ask", json={"question": "Which clinics have available diagnostics in Kenya?"})
    assert response.status_code == 401


def test_agent_returns_multi_tool_grounded_answer():
    response = client.post(
        "/agent/ask",
        headers={"Authorization": f"Bearer {operator_token()}"},
        json={"question": "Which clinics have available diagnostics in Kenya?"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["grounded"] is True
    assert body["tools_called"] == ["find_available_clinics", "search_clinics"]
    assert "Nairobi" in body["answer"]


def test_agent_honestly_declines_questions_outside_catalog():
    response = client.post(
        "/agent/ask",
        headers={"Authorization": f"Bearer {operator_token()}"},
        json={"question": "What is the clinic's insurance reimbursement policy?"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["grounded"] is False
    assert body["tools_called"] == []
    assert "cannot answer this" in body["answer"]
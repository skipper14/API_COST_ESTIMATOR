from fastapi.testclient import TestClient

from secure_triage_api import app

client = TestClient(app)


def login(username: str = "operator", password: str = "operator-pass") -> str:
    response = client.post("/token", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_is_public_and_versioned():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"


def test_fulfilment_requires_authentication():
    response = client.post("/fulfilment", json={"order_id": "ORD-123", "destination_country": "KE", "item_count": 1})
    assert response.status_code == 401


def test_invalid_fulfilment_is_rejected():
    token = login()
    response = client.post(
        "/fulfilment",
        headers={"Authorization": f"Bearer {token}"},
        json={"order_id": "bad", "destination_country": "Kenya", "item_count": 0},
    )
    assert response.status_code == 422


def test_operator_cannot_access_admin_route():
    response = client.get("/admin/audit", headers={"Authorization": f"Bearer {login()}"})
    assert response.status_code == 403


def test_authenticated_fulfilment_returns_model_response():
    response = client.post(
        "/fulfilment",
        headers={"Authorization": f"Bearer {login()}"},
        json={"order_id": "ORD-123", "destination_country": "KE", "item_count": 2},
    )
    assert response.status_code == 200
    assert response.json()["warehouse"] == "Nairobi"
import pytest


@pytest.fixture
def customer_id(client):
    response = client.post("/customers", json={"full_name": "Jane Doe", "email": "jane@example.com"})
    return response.json()["id"]


def _policy_payload(**overrides):
    payload = {
        "policy_type": "CAR",
        "premium_amount": "100.50",
        "coverage_amount": "5000",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    }
    payload.update(overrides)
    return payload


def test_issue_policy(client, customer_id):
    response = client.post(f"/customers/{customer_id}/policies", json=_policy_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer_id
    assert body["status"] == "ACTIVE"
    assert body["policy_number"].startswith("POL-")


def test_issue_policy_for_nonexistent_customer(client):
    response = client.post("/customers/999/policies", json=_policy_payload())
    assert response.status_code == 404


def test_issue_policy_invalid_date_range_rejected(client, customer_id):
    response = client.post(
        f"/customers/{customer_id}/policies",
        json=_policy_payload(start_date="2026-12-31", end_date="2026-01-01"),
    )
    assert response.status_code == 422


def test_issue_policy_negative_premium_rejected(client, customer_id):
    response = client.post(
        f"/customers/{customer_id}/policies", json=_policy_payload(premium_amount="-10")
    )
    assert response.status_code == 422


def test_list_policies_filter_by_customer(client, customer_id):
    client.post(f"/customers/{customer_id}/policies", json=_policy_payload())
    other_customer = client.post(
        "/customers", json={"full_name": "John Smith", "email": "john@example.com"}
    ).json()["id"]
    client.post(f"/customers/{other_customer}/policies", json=_policy_payload(policy_type="HEALTH"))

    response = client.get("/policies", params={"customer_id": customer_id})
    assert response.status_code == 200
    policies = response.json()
    assert len(policies) == 1
    assert policies[0]["customer_id"] == customer_id


def test_list_policies_filter_by_type(client, customer_id):
    client.post(f"/customers/{customer_id}/policies", json=_policy_payload(policy_type="CAR"))
    client.post(f"/customers/{customer_id}/policies", json=_policy_payload(policy_type="HEALTH"))

    response = client.get("/policies", params={"policy_type": "HEALTH"})
    assert response.status_code == 200
    policies = response.json()
    assert len(policies) == 1
    assert policies[0]["policy_type"] == "HEALTH"


def test_get_customer_policies(client, customer_id):
    client.post(f"/customers/{customer_id}/policies", json=_policy_payload())
    response = client.get(f"/customers/{customer_id}/policies")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_customer_policies_for_nonexistent_customer(client):
    response = client.get("/customers/999/policies")
    assert response.status_code == 404


def test_update_policy(client, customer_id):
    policy_id = client.post(f"/customers/{customer_id}/policies", json=_policy_payload()).json()["id"]
    response = client.patch(f"/policies/{policy_id}", json={"premium_amount": "200.00"})
    assert response.status_code == 200
    assert response.json()["premium_amount"] == "200.00"


def test_cancel_policy(client, customer_id):
    policy_id = client.post(f"/customers/{customer_id}/policies", json=_policy_payload()).json()["id"]
    response = client.post(f"/policies/{policy_id}/cancel", json={"reason": "customer request"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CANCELLED"
    assert body["cancellation_reason"] == "customer request"
    assert body["cancelled_at"] is not None


def test_cannot_cancel_already_cancelled_policy(client, customer_id):
    policy_id = client.post(f"/customers/{customer_id}/policies", json=_policy_payload()).json()["id"]
    client.post(f"/policies/{policy_id}/cancel")
    response = client.post(f"/policies/{policy_id}/cancel")
    assert response.status_code == 409


def test_cannot_update_cancelled_policy(client, customer_id):
    policy_id = client.post(f"/customers/{customer_id}/policies", json=_policy_payload()).json()["id"]
    client.post(f"/policies/{policy_id}/cancel")
    response = client.patch(f"/policies/{policy_id}", json={"premium_amount": "1.00"})
    assert response.status_code == 409


def test_get_policy_not_found(client):
    response = client.get("/policies/999")
    assert response.status_code == 404

def test_create_customer(client):
    response = client.post(
        "/customers", json={"full_name": "Jane Doe", "email": "jane@example.com"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == "Jane Doe"
    assert body["email"] == "jane@example.com"
    assert "id" in body


def test_create_customer_duplicate_email_conflicts(client):
    client.post("/customers", json={"full_name": "Jane Doe", "email": "jane@example.com"})
    response = client.post("/customers", json={"full_name": "Jane Two", "email": "jane@example.com"})
    assert response.status_code == 409


def test_create_customer_invalid_email_rejected(client):
    response = client.post("/customers", json={"full_name": "Jane Doe", "email": "not-an-email"})
    assert response.status_code == 422


def test_get_customer_not_found(client):
    response = client.get("/customers/999")
    assert response.status_code == 404


def test_list_customers(client):
    client.post("/customers", json={"full_name": "Jane Doe", "email": "jane@example.com"})
    client.post("/customers", json={"full_name": "John Smith", "email": "john@example.com"})
    response = client.get("/customers")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_customer(client):
    created = client.post("/customers", json={"full_name": "Jane Doe", "email": "jane@example.com"})
    customer_id = created.json()["id"]
    response = client.patch(f"/customers/{customer_id}", json={"phone": "555-1234"})
    assert response.status_code == 200
    assert response.json()["phone"] == "555-1234"
    assert response.json()["full_name"] == "Jane Doe"


def test_update_customer_not_found(client):
    response = client.patch("/customers/999", json={"phone": "555-1234"})
    assert response.status_code == 404

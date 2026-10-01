def test_product_list_empty(client):
    response = client.get(
        "/api/v1/products"
    )

    assert response.status_code == 200
    assert response.get_json()["items"] == []


def test_non_admin_cannot_create_product(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/products",
        headers=auth_headers,
        json={
            "name": "Laptop",
            "price": 1000,
            "stock": 10,
        },
    )

    assert response.status_code == 403

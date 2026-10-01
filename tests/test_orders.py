from app.extensions import db
from app.models.product import Product


def create_product(app):
    with app.app_context():
        product = Product(
            name="Laptop",
            description="Test laptop",
            price=1000,
            stock=10,
            category="electronics",
        )

        db.session.add(product)
        db.session.commit()

        return product.id


def test_order_requires_auth(client):
    response = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                }
            ]
        },
    )

    assert response.status_code == 401


def test_empty_order_rejected(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/orders",
        headers=auth_headers,
        json={
            "items": []
        },
    )

    assert response.status_code == 400

from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models.product import Product
from app.models.user import User


def seed():
    app = create_app()

    with app.app_context():
        admin = User.query.filter_by(
            email="admin@example.com"
        ).first()

        if not admin:
            admin = User(
                email="admin@example.com",
                name="Administrator",
                role="admin",
            )

            admin.set_password("admin12345")

            db.session.add(admin)

        products = [
            {
                "name": "Laptop",
                "description": "15 inch business laptop",
                "price": Decimal("899.99"),
                "stock": 25,
                "category": "electronics",
            },
            {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse",
                "price": Decimal("29.99"),
                "stock": 100,
                "category": "electronics",
            },
            {
                "name": "Mechanical Keyboard",
                "description": "RGB mechanical keyboard",
                "price": Decimal("89.99"),
                "stock": 50,
                "category": "electronics",
            },
        ]

        for data in products:
            exists = Product.query.filter_by(
                name=data["name"]
            ).first()

            if not exists:
                db.session.add(
                    Product(**data)
                )

        db.session.commit()

        print("Database seeded successfully.")


if __name__ == "__main__":
    seed()

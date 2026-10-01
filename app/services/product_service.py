from sqlalchemy import or_

from app.extensions import db
from app.models.product import Product
from app.services import cache
from app.utils.errors import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


PRODUCT_CACHE_PREFIX = "product:"


def get_product(product_id):
    cache_key = f"{PRODUCT_CACHE_PREFIX}{product_id}"

    cached = cache.get(cache_key)

    if cached:
        return cached

    product = db.session.get(Product, product_id)

    if not product or not product.is_active:
        raise NotFoundError("Product not found")

    result = product.to_dict()

    cache.set(cache_key, result)

    return result


def list_products(
    page=1,
    per_page=20,
    search=None,
    category=None,
):
    query = Product.query.filter_by(is_active=True)

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
            )
        )

    if category:
        query = query.filter(
            Product.category == category
        )

    pagination = query.order_by(
        Product.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return {
        "items": [
            product.to_dict()
            for product in pagination.items
        ],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


def create_product(data):
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock", 0)

    if not name:
        raise ValidationError("name is required")

    if price is None:
        raise ValidationError("price is required")

    if stock < 0:
        raise ValidationError(
            "stock cannot be negative"
        )

    product = Product(
        name=name,
        description=data.get("description"),
        price=price,
        stock=stock,
        category=data.get("category"),
        is_active=data.get("is_active", True),
    )

    db.session.add(product)
    db.session.commit()

    return product.to_dict()


def update_product(product_id, data):
    product = db.session.get(Product, product_id)

    if not product:
        raise NotFoundError("Product not found")

    if "name" in data:
        product.name = data["name"]

    if "description" in data:
        product.description = data["description"]

    if "price" in data:
        product.price = data["price"]

    if "stock" in data:
        if data["stock"] < 0:
            raise ValidationError(
                "stock cannot be negative"
            )
        product.stock = data["stock"]

    if "category" in data:
        product.category = data["category"]

    if "is_active" in data:
        product.is_active = data["is_active"]

    db.session.commit()

    cache.delete(
        f"{PRODUCT_CACHE_PREFIX}{product_id}"
    )

    return product.to_dict()


def delete_product(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        raise NotFoundError("Product not found")

    product.is_active = False

    db.session.commit()

    cache.delete(
        f"{PRODUCT_CACHE_PREFIX}{product_id}"
    )


def ensure_stock(product, quantity):
    if quantity <= 0:
        raise ValidationError(
            "quantity must be greater than zero"
        )

    if product.stock < quantity:
        raise ConflictError(
            f"Insufficient stock for {product.name}"
        )

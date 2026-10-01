from decimal import Decimal

from app.extensions import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.services.product_service import ensure_stock
from app.utils.errors import (
    NotFoundError,
    ValidationError,
)


VALID_STATUSES = {
    "pending",
    "confirmed",
    "shipped",
    "delivered",
    "cancelled",
}


def create_order(user_id, items):
    if not items:
        raise ValidationError(
            "Order must contain at least one item"
        )

    order = Order(
        user_id=user_id,
        status="pending",
        total=Decimal("0.00"),
    )

    db.session.add(order)

    total = Decimal("0.00")

    for item in items:
        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if not product_id:
            raise ValidationError(
                "product_id is required"
            )

        if not isinstance(quantity, int):
            raise ValidationError(
                "quantity must be an integer"
            )

        product = db.session.get(
            Product,
            product_id,
        )

        if not product or not product.is_active:
            raise NotFoundError(
                f"Product {product_id} not found"
            )

        ensure_stock(product, quantity)

        unit_price = Decimal(str(product.price))
        subtotal = unit_price * quantity

        order_item = OrderItem(
            order=order,
            product_id=product.id,
            product_name=product.name,
            unit_price=unit_price,
            quantity=quantity,
            subtotal=subtotal,
        )

        product.stock -= quantity

        total += subtotal

        db.session.add(order_item)

    order.total = total

    db.session.commit()

    return order


def get_order(order_id, user_id=None, is_admin=False):
    order = db.session.get(Order, order_id)

    if not order:
        raise NotFoundError("Order not found")

    if not is_admin and order.user_id != user_id:
        raise NotFoundError("Order not found")

    return order


def list_orders(user_id=None, is_admin=False):
    query = Order.query

    if not is_admin:
        query = query.filter_by(user_id=user_id)

    return query.order_by(
        Order.created_at.desc()
    ).all()


def update_status(order_id, status):
    if status not in VALID_STATUSES:
        raise ValidationError(
            f"Invalid status. "
            f"Allowed: {sorted(VALID_STATUSES)}"
        )

    order = db.session.get(Order, order_id)

    if not order:
        raise NotFoundError("Order not found")

    order.status = status

    db.session.commit()

    return order

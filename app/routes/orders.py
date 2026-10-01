from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.services import order_service


orders_bp = Blueprint(
    "orders",
    __name__,
)


def current_user_id():
    return int(get_jwt_identity())


def is_admin():
    return get_jwt().get("role") == "admin"


@orders_bp.post("")
@jwt_required()
def create_order():
    data = request.get_json(silent=True) or {}

    order = order_service.create_order(
        current_user_id(),
        data.get("items", []),
    )

    return jsonify(order.to_dict()), 201


@orders_bp.get("")
@jwt_required()
def list_orders():
    orders = order_service.list_orders(
        user_id=current_user_id(),
        is_admin=is_admin(),
    )

    return jsonify(
        {
            "items": [
                order.to_dict()
                for order in orders
            ]
        }
    )


@orders_bp.get("/<int:order_id>")
@jwt_required()
def get_order(order_id):
    order = order_service.get_order(
        order_id,
        user_id=current_user_id(),
        is_admin=is_admin(),
    )

    return jsonify(order.to_dict())


@orders_bp.patch("/<int:order_id>/status")
@jwt_required()
def update_status(order_id):
    if not is_admin():
        from app.utils.errors import ForbiddenError

        raise ForbiddenError(
            "Admin access required"
        )

    data = request.get_json(silent=True) or {}

    order = order_service.update_status(
        order_id,
        data.get("status"),
    )

    return jsonify(order.to_dict())

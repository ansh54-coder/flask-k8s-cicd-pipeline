from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services import product_service
from app.utils.errors import ValidationError


products_bp = Blueprint(
    "products",
    __name__,
)


def require_admin():
    from flask_jwt_extended import get_jwt

    claims = get_jwt()

    if claims.get("role") != "admin":
        from app.utils.errors import ForbiddenError

        raise ForbiddenError(
            "Admin access required"
        )


@products_bp.get("")
def list_products():
    try:
        page = int(
            request.args.get("page", 1)
        )

        per_page = int(
            request.args.get("per_page", 20)
        )
    except ValueError:
        raise ValidationError(
            "page and per_page must be integers"
        )

    if page < 1:
        raise ValidationError(
            "page must be greater than zero"
        )

    if per_page < 1 or per_page > 100:
        raise ValidationError(
            "per_page must be between 1 and 100"
        )

    result = product_service.list_products(
        page=page,
        per_page=per_page,
        search=request.args.get("search"),
        category=request.args.get("category"),
    )

    return jsonify(result)


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    return jsonify(
        product_service.get_product(product_id)
    )


@products_bp.post("")
@jwt_required()
def create_product():
    require_admin()

    data = request.get_json(silent=True) or {}

    return jsonify(
        product_service.create_product(data)
    ), 201


@products_bp.patch("/<int:product_id>")
@jwt_required()
def update_product(product_id):
    require_admin()

    data = request.get_json(silent=True) or {}

    return jsonify(
        product_service.update_product(
            product_id,
            data,
        )
    )


@products_bp.delete("/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    require_admin()

    product_service.delete_product(product_id)

    return "", 204

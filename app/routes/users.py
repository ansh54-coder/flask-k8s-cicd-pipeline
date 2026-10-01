from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import db
from app.models.user import User
from app.utils.errors import (
    ConflictError,
    UnauthorizedError,
    ValidationError,
)


users_bp = Blueprint(
    "users",
    __name__,
)


@users_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email:
        raise ValidationError("email is required")

    if not password or len(password) < 8:
        raise ValidationError(
            "password must contain at least 8 characters"
        )

    if not name:
        raise ValidationError("name is required")

    if User.query.filter_by(email=email).first():
        raise ConflictError(
            "A user with this email already exists"
        )

    user = User(
        email=email,
        name=name,
        role="customer",
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
        },
    )

    return jsonify(
        {
            "user": user.to_dict(),
            "access_token": token,
        }
    ), 201


@users_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(
        email=email
    ).first()

    if not user or not user.check_password(password):
        raise UnauthorizedError(
            "Invalid email or password"
        )

    if not user.is_active:
        raise UnauthorizedError(
            "User account is inactive"
        )

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
        },
    )

    return jsonify(
        {
            "user": user.to_dict(),
            "access_token": token,
        }
    )


@users_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        int(user_id),
    )

    if not user:
        raise UnauthorizedError(
            "User not found"
        )

    return jsonify(user.to_dict())

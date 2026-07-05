from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models.organizer import OrganizerProfile, OrganizerStatus
from app.models.user import Role, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        phone=phone,
        role=Role.USER,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"user_id": user.id, "role": user.role.value},
    )

    return (
        jsonify(
            {
                "message": "User registered successfully",
                "token": token,
                "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role.value},
            }
        ),
        201,
    )


@auth_bp.route("/register/organizer", methods=["POST"])
def register_organizer():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    document_path = data.get("document_path")

    if not name or not email or not password or not document_path:
        return jsonify({"error": "name, email, password, and document_path are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        phone=phone,
        role=Role.ORGANIZER,
    )
    organizer_profile = OrganizerProfile(
        user=user,
        document_path=document_path,
        status=OrganizerStatus.PENDING,
    )
    db.session.add(user)
    db.session.add(organizer_profile)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"user_id": user.id, "role": user.role.value},
    )

    return (
        jsonify(
            {
                "message": "Organizer registered successfully",
                "token": token,
                "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role.value},
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"user_id": user.id, "role": user.role.value},
    )

    return jsonify(
        {
            "message": "Login successful",
            "token": token,
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role.value},
        }
    )

from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, get_jwt, jwt_required

from app import db
from app.models.organizer import OrganizerProfile, OrganizerStatus
from app.models.user import Role

moderator_bp = Blueprint("moderator", __name__, url_prefix="/api/moderator")


def _require_moderator():
    claims = get_jwt()
    if claims.get("role") != Role.MODERATOR.value:
        return jsonify({"error": "forbidden"}), 403
    return None


@moderator_bp.route("/pending", methods=["GET"])
@jwt_required()
def list_pending_organizers():
    forbidden = _require_moderator()
    if forbidden:
        return forbidden

    pending_profiles = OrganizerProfile.query.filter_by(status=OrganizerStatus.PENDING).all()
    return jsonify(
        {
            "pending_organizers": [
                {
                    "id": profile.id,
                    "user_id": profile.user_id,
                    "name": profile.user.name if profile.user else None,
                    "email": profile.user.email if profile.user else None,
                    "document_path": profile.document_path,
                    "status": profile.status.value,
                }
                for profile in pending_profiles
            ]
        }
    )


@moderator_bp.route("/approve/<int:user_id>", methods=["POST"])
@jwt_required()
def approve_organizer(user_id):
    forbidden = _require_moderator()
    if forbidden:
        return forbidden

    profile = OrganizerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "organizer profile not found"}), 404

    profile.status = OrganizerStatus.APPROVED
    profile.rejection_reason = None
    db.session.commit()

    return jsonify({"message": "organizer approved", "user_id": user_id})


@moderator_bp.route("/reject/<int:user_id>", methods=["POST"])
@jwt_required()
def reject_organizer(user_id):
    forbidden = _require_moderator()
    if forbidden:
        return forbidden

    data = request.get_json(silent=True) or {}
    rejection_reason = data.get("rejection_reason")

    if not rejection_reason:
        return jsonify({"error": "rejection_reason is required"}), 400

    profile = OrganizerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "organizer profile not found"}), 404

    profile.status = OrganizerStatus.REJECTED
    profile.rejection_reason = rejection_reason
    db.session.commit()

    return jsonify({"message": "organizer rejected", "user_id": user_id})

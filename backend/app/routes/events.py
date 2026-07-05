from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app import db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.organizer import OrganizerProfile, OrganizerStatus
from app.models.user import Role, User

events_bp = Blueprint("events", __name__, url_prefix="/api/events")


def _require_role(expected_role):
    claims = get_jwt()
    if claims.get("role") != expected_role:
        return jsonify({"error": "forbidden"}), 403
    return None


@events_bp.route("", methods=["POST"])
@jwt_required()
def create_event():
    forbidden = _require_role(Role.ORGANIZER.value)
    if forbidden:
        return forbidden

    data = request.get_json(silent=True) or {}
    user_id = get_jwt().get("user_id")
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "user not found"}), 404

    profile = OrganizerProfile.query.filter_by(user_id=user_id).first()
    if not profile or profile.status != OrganizerStatus.APPROVED:
        return jsonify({"error": "organizer not approved"}), 403

    title = data.get("title")
    description = data.get("description")
    venue = data.get("venue")
    event_date = data.get("event_date")
    total_seats = data.get("total_seats")
    auto_redistribute = data.get("auto_redistribute", True)

    if not title or not venue or not event_date or total_seats is None:
        return jsonify({"error": "title, venue, event_date, and total_seats are required"}), 400

    try:
        event_date_obj = datetime.fromisoformat(event_date)
    except ValueError:
        return jsonify({"error": "event_date must be a valid ISO datetime"}), 400

    event = Event(
        organizer_id=user_id,
        title=title,
        description=description,
        venue=venue,
        event_date=event_date_obj,
        total_seats=int(total_seats),
        available_seats=int(total_seats),
        auto_redistribute=bool(auto_redistribute),
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "event created", "event": event_to_dict(event)}), 201


@events_bp.route("", methods=["GET"])
def list_events():
    events = Event.query.order_by(Event.event_date.asc()).all()
    return jsonify({"events": [event_to_dict(event) for event in events]})


@events_bp.route("/<int:event_id>/book", methods=["POST"])
@jwt_required()
def book_event(event_id):
    forbidden = _require_role(Role.USER.value)
    if forbidden:
        return forbidden

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "event not found"}), 404

    user_id = get_jwt().get("user_id")
    existing_booking = Booking.query.filter_by(event_id=event_id, user_id=user_id).first()
    if existing_booking:
        return jsonify({"error": "booking already exists for this user"}), 409

    if event.available_seats > 0:
        status = BookingStatus.CONFIRMED
        event.available_seats -= 1
    else:
        status = BookingStatus.WAITLISTED

    booking = Booking(event_id=event_id, user_id=user_id, status=status)
    db.session.add(booking)
    db.session.commit()

    return jsonify({"message": "booking created", "booking_status": status.value, "booking_id": booking.id})


@events_bp.route("/<int:event_id>/cancel/<int:booking_id>", methods=["POST"])
@jwt_required()
def cancel_booking(event_id, booking_id):
    forbidden = _require_role(Role.USER.value)
    if forbidden:
        return forbidden

    user_id = get_jwt().get("user_id")
    booking = Booking.query.filter_by(id=booking_id, event_id=event_id, user_id=user_id).first()
    if not booking:
        return jsonify({"error": "booking not found"}), 404

    if booking.status == BookingStatus.CANCELLED:
        return jsonify({"error": "booking already cancelled"}), 409

    original_status = booking.status
    booking.status = BookingStatus.CANCELLED
    if original_status == BookingStatus.CONFIRMED:
        if booking.event and booking.event.available_seats < booking.event.total_seats:
            booking.event.available_seats += 1
    db.session.commit()

    return jsonify({"message": "booking cancelled", "booking_id": booking.id})

def event_to_dict(event):
    return {
        "id": event.id,
        "organizer_id": event.organizer_id,
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "event_date": event.event_date.isoformat(),
        "total_seats": event.total_seats,
        "available_seats": event.available_seats,
        "auto_redistribute": event.auto_redistribute,
    }

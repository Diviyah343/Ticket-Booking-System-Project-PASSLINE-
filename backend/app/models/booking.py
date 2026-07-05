import enum
from datetime import datetime

from app import db


class BookingStatus(enum.Enum):
    CONFIRMED = "CONFIRMED"
    WAITLISTED = "WAITLISTED"
    CLAIM_PENDING = "CLAIM_PENDING"
    CANCELLED = "CANCELLED"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(
        db.Enum(BookingStatus, native_enum=False),
        default=BookingStatus.CONFIRMED,
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    claim_expires_at = db.Column(db.DateTime, nullable=True)

    event = db.relationship("Event", back_populates="bookings")
    user = db.relationship("User", back_populates="bookings")

    def __repr__(self):
        return f"<Booking {self.id}>"

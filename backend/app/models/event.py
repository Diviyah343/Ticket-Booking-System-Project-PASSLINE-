from datetime import datetime

from app import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    auto_redistribute = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    organizer = db.relationship("User", back_populates="events")
    bookings = db.relationship(
        "Booking",
        back_populates="event",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Event {self.title}>"

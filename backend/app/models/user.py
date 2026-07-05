import enum

from app import db


class Role(enum.Enum):
    USER = "USER"
    ORGANIZER = "ORGANIZER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    role = db.Column(db.Enum(Role, native_enum=False), default=Role.USER, nullable=False)

    organizer_profile = db.relationship(
        "OrganizerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    events = db.relationship(
        "Event",
        back_populates="organizer",
        cascade="all, delete-orphan",
    )
    bookings = db.relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.email}>"

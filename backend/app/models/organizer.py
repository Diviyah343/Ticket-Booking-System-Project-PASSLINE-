import enum

from app import db


class OrganizerStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class OrganizerProfile(db.Model):
    __tablename__ = "organizer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    document_path = db.Column(db.String(255), nullable=True)
    status = db.Column(
        db.Enum(OrganizerStatus, native_enum=False),
        default=OrganizerStatus.PENDING,
        nullable=False,
    )
    rejection_reason = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="organizer_profile")

    def __repr__(self):
        return f"<OrganizerProfile {self.user_id}>"

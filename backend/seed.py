from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import Role, User


def seed_users():
    app = create_app()
    with app.app_context():
        users_to_create = [
            {
                "name": "Admin",
                "email": "admin@passline.com",
                "password": "admin123",
                "role": Role.ADMIN,
            },
            {
                "name": "Moderator",
                "email": "moderator@passline.com",
                "password": "mod123",
                "role": Role.MODERATOR,
            },
        ]

        for user_data in users_to_create:
            existing_user = User.query.filter_by(email=user_data["email"]).first()
            if existing_user:
                continue

            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
                role=user_data["role"],
            )
            db.session.add(user)

        db.session.commit()


if __name__ == "__main__":
    seed_users()

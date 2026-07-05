from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config


db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from .models.user import User
    from .models.organizer import OrganizerProfile
    from .models.event import Event
    from .models.booking import Booking
    from .routes.auth import auth_bp
    from .routes.events import events_bp
    from .routes.moderator import moderator_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(moderator_bp)

    return app

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "development-fallback-key"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///citizen_service.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "main.admin_login"

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

        from app.models import Admin

        admin_username = os.getenv(
            "ADMIN_USERNAME",
            "admin"
        )

        admin_password = os.getenv(
            "ADMIN_PASSWORD",
            "Admin@123"
        )

        existing_admin = Admin.query.filter_by(
            username=admin_username
        ).first()

        if not existing_admin:
            admin = Admin(
                username=admin_username,
                password_hash=generate_password_hash(
                    admin_password
                )
            )

            db.session.add(admin)
            db.session.commit()

    return app
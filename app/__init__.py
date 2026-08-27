from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "development-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///citizen_service.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "main.admin_login"

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

        from app.models import Admin

        existing_admin = Admin.query.filter_by(
            username="admin"
        ).first()

        if not existing_admin:
            admin = Admin(
                username="admin",
                password_hash=generate_password_hash(
                    "Admin@123"
                )
            )

            db.session.add(admin)
            db.session.commit()

    return app
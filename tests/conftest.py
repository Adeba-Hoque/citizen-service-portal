import pytest

from app import create_app, db


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key"
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        # create the default admin for tests
        from app.models import Admin
        from werkzeug.security import generate_password_hash

        admin = Admin(
            username="admin",
            password_hash=generate_password_hash("Admin@123")
        )

        db.session.add(admin)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
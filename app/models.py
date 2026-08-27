from datetime import datetime
from flask_login import UserMixin
from app import db


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    def __repr__(self):
        return f"<Admin {self.username}>"


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    reference = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    citizen_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Medium"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Submitted"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<ServiceRequest {self.reference}>"

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    admin_username = db.Column(
        db.String(80),
        nullable=False
    )

    request_reference = db.Column(
        db.String(30),
        nullable=False
    )

    action = db.Column(
        db.String(100),
        nullable=False
    )

    old_value = db.Column(
        db.String(150),
        nullable=True
    )

    new_value = db.Column(
        db.String(150),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<AuditLog {self.action}>"
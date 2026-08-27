from datetime import datetime
from app import db


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
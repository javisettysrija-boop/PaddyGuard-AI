from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    language = db.Column(
        db.String(10),
        default="en"
    )

    location = db.Column(
        db.String(120),
        default=""
    )

    diagnoses = db.relationship(
        "Diagnosis",
        backref="user",
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )


class Diagnosis(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    image_name = db.Column(
        db.String(255),
        nullable=False
    )

    disease = db.Column(
        db.String(120),
        nullable=False
    )

    confidence = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Alert(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    alert_type = db.Column(
        db.String(80),
        nullable=False
    )

    message = db.Column(
        db.String(500),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
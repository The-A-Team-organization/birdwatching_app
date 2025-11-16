from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false
from sqlalchemy.orm.strategy_options import defaultload
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False, default="user")
    bird_pictures = db.relationship("BirdPictures", backref="user", lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_role(self, role):
        self.role = role


class BirdPictures(db.Model):
    __tablename__ = "bird_pictures"

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255), nullable=False)
    is_protected = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def set_password(self, password: str):
        if password:
            self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class HunterIP(db.Model):
    __tablename__ = "hunter_ips"

    id = db.Column(db.Integer, primary_key=True)
    ipaddr = db.Column(db.String(255), unique=True, nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    def set_ip(self, ip: str):
        self.ipaddr = generate_password_hash(ip)

    def check_ip(self, ip: str) -> bool:
        return check_password_hash(self.ipaddr, ip)

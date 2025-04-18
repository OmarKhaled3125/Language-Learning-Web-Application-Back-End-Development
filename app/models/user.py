from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verification_code_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

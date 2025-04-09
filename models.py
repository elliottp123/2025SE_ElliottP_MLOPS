from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
import bcrypt
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary)
    developer_tag = db.Column(db.String(50), unique=True, nullable=False)
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_verified = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(40), unique=True)
    api_enabled = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def generate_api_key(self):
        self.api_key = f"dvlg_{secrets.token_hex(16)}"
        self.api_enabled = True
        return self.api_key


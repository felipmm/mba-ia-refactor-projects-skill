from database import db
from datetime import datetime
import hashlib
import secrets

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        salt = secrets.token_hex(16)
        digest = hashlib.sha256((salt + pwd).encode()).hexdigest()
        self.password = f"{salt}:{digest}"

    def check_password(self, pwd):
        if ':' not in self.password:
            return False
        salt, digest = self.password.split(':', 1)
        return hashlib.sha256((salt + pwd).encode()).hexdigest() == digest

    def is_admin(self):
        return self.role == 'admin'

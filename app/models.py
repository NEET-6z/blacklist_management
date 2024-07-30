from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.app import login_manager
from app.db import db


class BlackList(db.Model):
    __tablename__ = "blacklist"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    reason = db.Column(db.Text(255),default="",nullable=False)
    level = db.Column(db.Integer)
    state = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'))

class Manager(UserMixin,db.Model):
    __tablename__ = 'manager'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50))
    password_hash = db.Column(db.String(511), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    role = db.Column(db.Integer, default=1, nullable=False) 

    blacklist = db.relationship('BlackList', backref='manager', lazy='dynamic')

    
    def __repr__(self):
        return self.name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Manager.query.get(int(user_id))

#114-0005
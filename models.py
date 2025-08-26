from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __bind_key__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # ユーザーID（未ログイン時はnull）
    title = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default="Med")
    status = db.Column(db.String(10), nullable=False, default="todo")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    start_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)

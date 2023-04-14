from datetime import datetime

from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    tg = db.Column(db.Boolean, default=0)

    def __repr__(self):
        return f"Note('{self.title}', '{self.content}', '{self.created_at}')"
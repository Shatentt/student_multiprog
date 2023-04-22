from datetime import datetime

import sqlalchemy
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Note(SqlAlchemyBase):
    __tablename__ = 'notes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(100))
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
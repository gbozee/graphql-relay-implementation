from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ModelMixin(object):
    def save(self):
        db.session.add(self)
        db.session.commit()


class UserModel(ModelMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    last_name = db.Column(db.String)

    def __repr__(self):
        return "<UserModel %s>" % self.name

    

class TodoModel(ModelMixin, db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String)
    completed = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel',
                           backref=db.backref('todos', lazy='dynamic'))

    def __repr__(self):
        return "<TodoModel %s>" % self.task
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 2 10:34:10 2020

@author: jpick
"""
from datetime import datetime, date
from . import db, login, ma
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import column_property

@login.user_loader
def load_user(id):
    user=User.query.get(int(id))
    return user
       

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64), index=True, nullable=False, unique=True)
    first_name=db.Column(db.String(256), nullable=False)
    last_name=db.Column(db.String(256), nullable=False)
    full_name=column_property(first_name + " " + last_name)
    employee_id=db.Column(db.String(20), nullable=False, unique=True)
    email=db.Column(db.String(120), index=True, nullable=False, unique=True)
    password_hash=db.Column(db.String(256))
    access_level=db.Column(db.Integer, nullable=False, default=1)
    
    
    def set_password (self,password):
        self.password_hash=generate_password_hash(password)
        
    def check_password (self,password):
        return check_password_hash(self.password_hash,password)
    
    def set_access (self, level):
        self.access_level=level
    
    
    def __repr__(self):
        return 'User {}'.format(self.username)  

class Task(db.Model):
    __tablename__ = 'task'
    __table_args__ = {'extend_existing': True}
    task_id= db.Column(db.Integer,primary_key=True)
    person_created= db.Column(db.String(20), db.ForeignKey('user.employee_id'), nullable=False)
    datetime_created= db.Column(db.DateTime, nullable=False)
    person_who_assigned= db.Column(db.String(20), db.ForeignKey('user.employee_id'), nullable=False)
    datetime_assigned= db.Column(db.DateTime, nullable=False)
    person_assigned= db.Column(db.String(20), db.ForeignKey('user.employee_id'), nullable=False)
    datetime_due= db.Column(db.Date)
    task = db.Column(db.String(128), nullable=False)
    task_description= db.Column(db.String(2048), nullable=False)
    task_completed_datetime = db.Column(db.DateTime)
    task_completed=db.Column(db.Boolean, nullable=False, default=False)
    person_completed=db.Column(db.String(20), db.ForeignKey('user.employee_id'))
    priority=db.Column(db.Boolean, nullable=False, default=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.event_id'))

class Event(db.Model):
    __tablename__= 'event'
    __table_args__ = {'extend_existing': True}
    event_id= db.Column(db.Integer,primary_key=True)
    event_type=db.Column(db.String(128), nullable=False)
    student_id=db.Column(db.String(64))
    school= db.Column(db.String(128), nullable=False)
    summary= db.Column(db.String(8192), nullable=False)
    role_contacted=db.Column(db.String(128), nullable=False)
    name_contacted=db.Column(db.String(128))
    #other_description=db.Column(db.String(128))
    complete_timestamp= db.Column(db.DateTime, nullable=False)
    person_completed=db.Column(db.String(20), db.ForeignKey('user.employee_id'), nullable=False)
    last_edited_timestamp=db.Column(db.DateTime, nullable=False)
    person_last_edited=db.Column(db.String(20), db.ForeignKey('user.employee_id'), nullable=False)
    follow_up_task= db.Column(db.String(128))
    follow_up_task_id= db.Column(db.Integer, db.ForeignKey('task.task_id'))
    
class School(db.Model):
    __tablename__= 'school'
    school_id=db.Column(db.Integer, primary_key=True)
    school_name=db.Column(db.String(256), nullable=False)
    
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model= User
        load_instance=True
        fields=['id', 'username', 'first_name', 'last_name', 'employee_id']
        
class TaskSchema(ma.SQLAlchemySchema):
    class Meta:
        model= Task
        load_instance=True
        include_fk=True
        fields=['task_id', 'person_assigned', 'person_who_assigned', 'task', 'task_description', 'datetime_due', 'datetime_assigned', 'priority', 'task_completed']

class EventSchema(ma.SQLAlchemySchema):
    class Meta:
        model=Event
        load_instance=True
        include_fk=True
        fields=['event_id', 'event_type', 'student_id', 'school', 'summary', 'role_contacted', 'name_contacted', 'complete_timestamp', \
        'person_completed', 'last_edited_timestamp', 'person_last_edited', 'follow_up_task_id']
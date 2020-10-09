# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 10:03:44 2019

@author: jpick
"""

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, DateField,  TextAreaField, HiddenField, SelectMultipleField
from wtforms.fields.html5 import DateTimeField
from wtforms.widgets.html5 import DateTimeInput
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional
    
class TaskForm(FlaskForm):
    person_assigned = SelectField('person_assigned', validators=[InputRequired()], id='person_assigned')
    datetime_due = DateField('datetime_due', validators=[Optional()], id='datetime_due')
    task = SelectField('task', choices=[('email'), ('phone call')], validators=[InputRequired()], id='task')
    task_description = TextAreaField('task_description', validators=[InputRequired()], id='task_description')
    priority = BooleanField('priority', validators=[Optional()], id='priority')

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(html_tag='ol', prefix_label=False)
    option_widget = CheckboxInput() 

        
class EventForm(FlaskForm):  
    event_type=SelectField(label='Event Type ', choices=[('conference'), ('email'), ('meeting'), ('phone call'), ('training')], validators=[InputRequired()], id='event_type')
    student_id=StringField(label='Student ID (optional) ', validators=[Optional(), Length(min=6, max=6)], id='student_id')
    school=SelectField(label='School', validators=[InputRequired()], id='school')
    summary=TextAreaField(label='Summary ', validators=[InputRequired()], id='summary')
    role_contacted=SelectField('Role of person contacted ',  choices=[('Administrator'), ('Advocate/Lawyer'), ('AT Specialist'), ('Behavior specialist/RBT'), ('Classroom Teacher'), ('DHH'), ('Gifted Teacher'), ('OT/PT'), ('Parent/Guardian'), ('SLP'), ('VI Teacher'), ('Other')], validators=[InputRequired()], id='role_contacted')
    name_contacted=StringField('Name of Primary Contact for Event (optional)', validators=[Optional()], id='name_contacted')
    person_completed=SelectField('Person who completed Event', validators=[InputRequired()], id='person_completed')
    
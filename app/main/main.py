from flask import Blueprint, render_template, flash, redirect, request, jsonify, json, make_response, send_file, send_from_directory, url_for
from app.models import User, Task, Event, School, UserSchema, TaskSchema, EventSchema
from app import db, ma
from flask import current_app as app
from flask_login import current_user, login_user, login_required, logout_user
from .forms import TaskForm, EventForm
from datetime import datetime, date, timedelta
from utils import date_sql, datetime_sql
from sqlalchemy.orm import load_only
from sqlalchemy import or_, func, and_
from math import pi
import pandas as pd
import numpy as np
from bokeh.models import HoverTool, Plot, Grid, LinearAxis, FactorRange, Range1d, LabelSet 
from bokeh.plotting import figure
from bokeh.palettes import Category20c
from bokeh.models.glyphs import VBar
from bokeh.models.sources import ColumnDataSource
from bokeh.embed import components
from bokeh.transform import cumsum

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_bp.route('/main/contact-tracker', methods=['GET', 'POST'])
@login_required
def contact_tracker():
    tasks=Task.query.filter_by(person_assigned=current_user.employee_id).order_by(Task.datetime_assigned).all()
    employees=User.query.filter(User.id>0).order_by(User.last_name).all()
    employee_task_list=[]
    employee_event_list=[]
    red_list=[]
    for task in tasks:
        employee_assigned=User.query.filter_by(employee_id=task.person_who_assigned).first()
        if task.datetime_due and task.datetime_due < date.today() and not task.task_completed:
            red_list.append(True)
        else:
            red_list.append(False)
        if employee_assigned:
            employee_task_list.append(employee_assigned.full_name)
        else:
            employee_task_list.append(task.person_who_assigned)
    events=Event.query.filter_by(person_completed=current_user.employee_id).order_by(Event.complete_timestamp.desc()).limit(50).all()
    for event in events:
        employee_name=User.query.filter_by(employee_id=event.person_last_edited).first()
        if employee_name:
            employee_event_list.append(employee_name.full_name)
        else:
            employee_event_list.append(event.person_last_edited)
    schools=School.query.order_by(School.school_name).all()
    return render_template('main_page.html', user=current_user, tasks=tasks, employees=employees, employee_list=employee_task_list, employee_event_list=employee_event_list, red_list=red_list, events=events, schools=schools)

@main_bp.route('/main/task-create', methods=['GET', 'POST'])
@login_required
def task_maker():
    form=TaskForm()
    form.person_assigned.choices = [(e.employee_id, e.full_name) for e in User.query.order_by('last_name')]
    if form.validate_on_submit():
        red=False
        dt = datetime.now()
        x= dt.strftime("%Y-%m-%d %H:%M:%S")
        new_task=Task(person_created=current_user.employee_id, datetime_created=datetime_sql(x), person_who_assigned=current_user.employee_id, datetime_assigned=datetime_sql(x), \
                        person_assigned=form.person_assigned.data, task=form.task.data, task_description=form.task_description.data)
        if form.datetime_due.data:
            new_task.datetime_due=form.datetime_due.data
            if form.datetime_due.data < date.today():
                    red=True
        if form.priority.data:
            new_task.priority=True
        db.session.add(new_task)
        db.session.commit()
        employee=User.query.filter_by(employee_id=new_task.person_who_assigned).first()
        if employee:
            full_name_for_table=employee.full_name
        else:
            full_name_for_table=new_task.person_who_assigned
        return {'success' : 'New task created.', 'task_id' : new_task.task_id, 'datetime_assigned' : new_task.datetime_assigned, 'person_who_assigned' : new_task.person_who_assigned, \
                'person_assigned' : new_task.person_assigned, 'task' : new_task.task, 'task_description' : new_task.task_description, 'datetime_due' : new_task.datetime_due, \
                'priority' : new_task.priority, 'task_completed' : False, 'person_assigned_previous' : new_task.person_assigned, 'full_name_for_table' : full_name_for_table, 'red' : red}
    if request.method=='POST':
        return {'error': 'Problem submitting form. Make sure all required fields are entered.', 'task_description_error' : form.task_description.errors, \
                'task_datetime_due_error' : form.datetime_due.errors}
    return render_template('task_create.html', user=current_user, form=form, edit=None, task=None)
    
@main_bp.route('/main/task-edit/<task_id>', methods=['GET', 'POST'])
@login_required
def task_editor(task_id):
    try:
        task_id=int(task_id.split('_')[2])
        task=Task.query.filter_by(task_id=task_id, task_completed=False).first()
        if task is None:
            flash('This task either does not exist or is completed and hence not editable.', 'danger')
            return redirect(url_for('main_bp.contact_tracker'))
        if task.person_assigned != current_user.employee_id and current_user.access_level<2:
            flash('This task is not assigned to you and you do not have permission to edit this task.', 'danger')
            return redirect(url_for('main_bp.contact_tracker'))
        form=TaskForm()
        form.person_assigned.choices = [(e.employee_id, e.full_name) for e in User.query.order_by('last_name')]
        if form.validate_on_submit():
            red=False
            person_last_assigned=task.person_assigned
            person_now_assigned=form.person_assigned.data
            if person_last_assigned != person_now_assigned:
                dt = datetime.now()
                x= dt.strftime("%Y-%m-%d %H:%M:%S")
                task.person_assigned=form.person_assigned.data
                task.person_who_assigned=current_user.employee_id
                task.datetime_assigned=datetime_sql(x)
            if form.datetime_due.data:
                task.datetime_due=form.datetime_due.data
                if form.datetime_due.data < date.today():
                    red=True
            task.task_description=form.task_description.data
            task.task=form.task.data
            if form.priority.data:
                task.priority=True
            else:
                task.priority=False
            employee=User.query.filter_by(employee_id=task.person_who_assigned).first()
            if employee:
                full_name_for_table=employee.full_name
            else:
                full_name_for_table=task.person_who_assigned
            db.session.commit()
            
            return {'success' : 'Task successfully updated.', 'task_id' : task.task_id, 'datetime_assigned' : task.datetime_assigned, 'person_who_assigned' : task.person_who_assigned, \
                    'person_assigned' : task.person_assigned, 'task' : task.task, 'task_description' : task.task_description, 'datetime_due' : task.datetime_due, \
                    'priority' : task.priority, 'task_completed' : False, 'person_assigned_previous' : person_last_assigned, 'full_name_for_table' : full_name_for_table, 'red' : red}      
        if request.method=='POST':
            return {'error': 'Problem submitting form. Make sure all required fields are entered.', 'task_description_error' : form.task_description.errors, \
                'task_datetime_due_error' : form.datetime_due.errors}
        return render_template('task_create.html', user=current_user, form=form, edit=True, task=task)
    except:
        flash('An error occurred in the request, and you have been redirected to your main page.', 'danger')
        return redirect(url_for('main_bp.contact_tracker'))

   
@main_bp.route('/main/user-fetch/<employee_id>', methods=['GET'])
@login_required
def user_fetch(employee_id): 
    try:
        employee=User.query.filter_by(employee_id=employee_id).first()
        if employee is None:
            return {'error' : 'This employee is not in the database'}
        task=Task.query.filter_by(person_assigned=employee_id).first()
        if task is None:
            return {'error' : 'This employee has not tasks to view currently.'}
        fields=['task_id', 'datetime_assigned', 'person_assigned', 'person_who_assigned', 'task', 'task_description', 'datetime_due', 'priority', 'task_completed']
        tasks=Task.query.filter_by(person_assigned=employee_id).options(load_only(*fields)).order_by(Task.datetime_assigned).all()
        red_list=[]
        for task in tasks:
            if task.datetime_due and task.datetime_due < date.today() and not task.task_completed:
                red_list.append(True)
            else:
                red_list.append(False)
        tasks_schema=TaskSchema(many=True)
        output=tasks_schema.dump(tasks)
        employees=User.query.all()
        name_id_crosswalk={}
        for e in employees:
            current_dict={e.employee_id : e.full_name}
            name_id_crosswalk.update(current_dict)
        for o in output:
            if o['person_who_assigned'] in name_id_crosswalk: 
                current_dict={'full_name_person_who_assigned' : name_id_crosswalk['{}'.format(o['person_who_assigned'])]}
            else:
                current_dict={'full_name_person_who_assigned' : o['person_who_assigned']}
            o.update(current_dict)
        for index, o in enumerate(output):
            if red_list[index]:
               current_dict={'red' : True}
            else:
               current_dict={'red' : False} 
            o.update(current_dict)
        return jsonify({'test' : output})
    except:
        return {'error' : "An error occurred while fetching this user's task data."}

@main_bp.route('/main/complete-task-view/<task_id>', methods=['GET'])
@login_required
def task_viewer(task_id):
    try:
        task_id=int(task_id.split('_')[2])
        task=Task.query.filter_by(task_id=task_id).first()
        if task is None:
            return {'error' : 'There was an error processing the task requested.'}
        else:
            employee_create=User.query.filter_by(employee_id=task.person_created).first()
            if employee_create:
                create_name_for_report=employee_create.full_name
            else:
                create_name_for_report=task.person_created
            employee_who_assigned=User.query.filter_by(employee_id=task.person_who_assigned).first()
            if employee_who_assigned:
                person_who_assign_name_for_report=employee_who_assigned.full_name
            else:
                person_who_assign_name_for_report=task.person_who_assigned
            employee_assigned=User.query.filter_by(employee_id=task.person_assigned).first()
            if employee_assigned:
                person_assigned_name_for_report=employee_assigned.full_name
            else:
                person_assigned_name_for_report=task.person_assigned
            if task.task_completed:
                employee_who_completed=User.query.filter_by(employee_id=task.person_completed).first()
                if employee_who_completed:
                   person_completed_name_for_report=employee_who_completed.full_name
                else:
                    person_completed_name_for_report=task.person_completed
            else:
                person_completed_name_for_report=None
            return {'success' : 'Full Task report downloaded', 'task_id' : task.task_id, 'datetime_assigned' : task.datetime_assigned, 'person_who_assigned' : task.person_who_assigned, \
                    'person_assigned' : task.person_assigned, 'task' : task.task, 'task_description' : task.task_description, 'datetime_due' : task.datetime_due, \
                    'priority' : task.priority, 'task_completed' : task.task_completed, 'create_name_for_report' : create_name_for_report, \
                    'person_who_assign_name_for_report' : person_who_assign_name_for_report, 'person_assigned_name_for_report' : person_assigned_name_for_report, \
                    'person_completed_name_for_report' : person_completed_name_for_report, 'datetime_created' : task.datetime_created, 'datetime_completed' : task.task_completed_datetime}
    except:
        return {'error' : 'There was an error processing the task requested.'}
        
        
    
        
@main_bp.route('/main/event-new', methods=['GET', 'POST'])
@login_required
def event_new():
    form=EventForm()
    form.school.choices = [(s.school_name) for s in School.query.order_by(School.school_name)]
    if current_user.access_level==1:
        del form.person_completed
    else:
        form.person_completed.choices = [(e.employee_id, e.full_name) for e in User.query.order_by('last_name')]
    if form.validate_on_submit():
        dt = datetime.now()
        x= dt.strftime("%Y-%m-%d %H:%M:%S")
        if current_user.access_level==1:
            person_completed=current_user.employee_id
        else:
            person_completed=form.person_completed.data
        new_event=Event(event_type=form.event_type.data, school=form.school.data, summary=form.summary.data, complete_timestamp=datetime_sql(x), \
        person_completed=person_completed, last_edited_timestamp=datetime_sql(x), person_last_edited=current_user.employee_id, \
        role_contacted=form.role_contacted.data)
        if form.student_id.data:
            new_event.student_id=form.student_id.data
        if form.name_contacted.data:
            new_event.name_contacted=form.name_contacted.data
        db.session.add(new_event)
        db.session.commit()
        return {'success' : 'Event Successfully Created!'}
        
    return render_template('event_boot.html', user=current_user, form=form, edit=None, task=None, event=None)  
        
 
@main_bp.route('/main/event-with-task/<task_id>', methods=['GET', 'POST'])
@login_required
def event_with_task(task_id):
    try:
        task_id=int(task_id.split('_')[2])
        task=Task.query.filter_by(task_id=task_id).first()
        if task is None:
            return {'error' : 'There was an error processing the task requested.'}
        else:
            form=EventForm()
            form.school.choices = [(s.school_name) for s in School.query.order_by(School.school_name)]
            if current_user.access_level==1:
                del form.person_completed
            else:
                form.person_completed.choices = [(e.employee_id, e.full_name) for e in User.query.order_by('last_name')]
            if form.validate_on_submit():
                dt = datetime.now()
                x= dt.strftime("%Y-%m-%d %H:%M:%S")
                if current_user.access_level==1:
                    person_completed=current_user.employee_id
                else:
                    person_completed=form.person_completed.data
                new_event=Event(event_type=form.event_type.data, school=form.school.data, summary=form.summary.data, complete_timestamp=datetime_sql(x), \
                person_completed=current_user.employee_id, last_edited_timestamp=datetime_sql(x), person_last_edited=current_user.employee_id, \
                role_contacted=form.role_contacted.data, follow_up_task_id=task.task_id)
                if form.student_id.data:
                    new_event.student_id=form.student_id.data
                if form.name_contacted.data:
                    new_event.name_contacted=form.name_contacted.data
                task.task_completed=True
                task.task_completed_datetime=datetime_sql(x)
                task.person_completed=person_completed
                task.event_id=new_event.event_id
                db.session.add(new_event)
                db.session.commit()
                return {'success' : 'Event Successfully Created!'}
            elif request.method=='POST':
                return {'error' : 'Must fill out all required fields.'}
            else:              
                return render_template('event_boot.html', user=current_user, form=form, edit=None, task=task, event=None)
    except:
        return {'error' : 'An error occurred while creating or editing this event.'}

@main_bp.route('/main/event-with-task-getter/<task_id>', methods=['GET'])
@login_required        
def event_with_task_getter(task_id):
    try:
        task_test_id=int(task_id.split('_')[2])
        task=Task.query.filter_by(task_id=task_test_id).first()
        if task is None:
            return {'error' : 'There was an error processing the task requested.'}
        else:
            return {'success' : 'Event form for task successfully loaded. Click Ok to continue.', 'id' : task_id}
    except:
        return {'error' : 'An error occurred while creating or editing this event.'}
        
@main_bp.route('/main/event-searcher', methods=['POST'])
@login_required
def event_searcher():
    try:
        results=None
        id_provided=False
        name_provided=False
        if request.form.get('school') is None:
            schools=School.query.all()
            school_list=[]
            for school in schools:
                school_list.append(school.school_name)
        else:
            school_list=request.form.getlist('school')
        if request.form.get('employee') is None:
            employees=User.query.all()
            employee_list=[]
            for employee in employees:
                employee_list.append(employee.employee_id)
        else:
            employee_list=request.form.getlist('employee')
        if request.form.get('role_contacted') is None:
            roles=False
        else:
            roles=True
            role_list=request.form.getlist('role_contacted')
        if request.form.get('start_date') is None:
            start=date(2000, 1,1, 0,0,0)
        else:
            start=request.form.get('start_date')
        if request.form.get('end_date') is None:
            end_date=date(datetime.now().year, datetime.now().month, datetime.now().day, 23, 59, 59)
        else:
            end_date=request.form.get('end_date')
        if request.form.get('student_id').strip() is not None and request.form.get('student_id').strip()!="":
            student_id=request.form.get('student_id').strip()
            id_provided=True
        if request.form.get('name_contacted').strip() is not None and request.form.get('name_contacted').strip()!="":
            name_contacted=request.form.get('name_contacted').strip()
            name_provided=True
        if roles:
            if id_provided:
                if name_provided:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), or_(Event.role_contacted==r for r in role_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date, Event.student_id==student_id, Event.name_contacted==name_contacted).order_by(Event.complete_timestamp).limit(1000).all()
                else:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), or_(Event.role_contacted==r for r in role_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date, Event.student_id==student_id).order_by(Event.complete_timestamp).limit(1000).all()
            else:
                if name_provided:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), or_(Event.role_contacted==r for r in role_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date, Event.name_contacted==name_contacted).order_by(Event.complete_timestamp).limit(1000).all()
                else:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), or_(Event.role_contacted==r for r in role_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date).order_by(Event.complete_timestamp).limit(1000).all()
        else:
            if id_provided:
                if name_provided:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date, Event.student_id==student_id, Event.name_contacted==name_contacted).order_by(Event.complete_timestamp).limit(1000).all()
                else:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date, Event.student_id==student_id).order_by(Event.complete_timestamp).limit(1000).all()
            else:
                if name_provided:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date, Event.name_contacted==name_contacted).order_by(Event.complete_timestamp).limit(1000).all()
                else:
                    results=Event.query.filter(or_(Event.school==s for s in school_list), or_(Event.person_completed==e for e in employee_list), Event.complete_timestamp>=start, (Event.complete_timestamp-timedelta(days=1))<=end_date).order_by(Event.complete_timestamp).limit(1000).all()
        events_schema=EventSchema(many=True)
        output=events_schema.dump(results)
        employees=User.query.all()
        name_id_crosswalk={}
        for e in employees:
            current_dict={e.employee_id : e.full_name}
            name_id_crosswalk.update(current_dict)
        for o in output:
            if o['person_completed'] in name_id_crosswalk: 
                current_dict={'person_name_completed' : name_id_crosswalk['{}'.format(o['person_completed'])]}
            else:
                current_dict={'person_name_completed' : o['person_completed']}
            o.update(current_dict)
            if o['person_last_edited'] in name_id_crosswalk:
                current_dict={'person_name_updated' : name_id_crosswalk['{}'.format(o['person_last_edited'])]}
            else:
                current_dict={'person_name_updated' : o['person_last_edited']}
            o.update(current_dict)
        return jsonify({'success' : 'The query was completed successfully', 'test' : output})
    except:
        return {'error' : 'An error occurred while processing the query'}

@main_bp.route('/main/event-editor/<event_id>', methods=['GET', 'POST'])
@login_required
def event_editor(event_id):
    try:
        event_id=int(event_id.split('_')[2])
        event=Event.query.filter_by(event_id=event_id).first()
        task=None
        if event is None:
            return {'error' : 'There was an error processing the event requested.'}
        else:
            form=EventForm()
            form.school.choices = [(s.school_name) for s in School.query.order_by(School.school_name)]
            if current_user.access_level==1:
                del form.person_completed
            else:
                form.person_completed.choices = [(e.employee_id, e.full_name) for e in User.query.order_by('last_name')]
            if event.follow_up_task_id:
                task=Task.query.filter_by(task_id=event.follow_up_task_id).first()
            if form.validate_on_submit():
                dt = datetime.now()
                x= dt.strftime("%Y-%m-%d %H:%M:%S")
                if current_user.access_level!=1:
                    person_completed=form.person_completed.data
                    if person_completed!=event.person_completed:
                        event.person_completed=person_completed  
                if form.student_id.data:
                    event.student_id=form.student_id.data
                else:
                    event.student_id=None
                if form.name_contacted.data:
                    event.name_contacted=form.name_contacted.data
                else:
                    event.name_contacted=None
                event.person_last_edited=current_user.employee_id
                event.last_edited_timestamp=datetime_sql(x)
                event.role_contacted=form.role_contacted.data
                event.event_type=form.event_type.data
                event.school=form.school.data
                event.summary=form.summary.data
                employee_edit=User.query.filter_by(employee_id=current_user.employee_id).first()
                if employee_edit:
                    name_for_edited=employee_edit.full_name
                else:
                    name_for_edited=current_user.employee_id
                employee_complete=User.query.filter_by(employee_id=event.person_completed).first()
                if employee_complete:
                    name_for_completion=employee_complete.full_name
                else:
                    name_for_completion=event.person_completed
                db.session.commit()
                return {'success' : 'Event Successfully Edited!', 'last_edited_timestamp' : event.last_edited_timestamp, 'name_for_edited' : name_for_edited, \
                'name_for_completion' : name_for_completion, 'event_type' : event.event_type, 'role_contacted' : event.role_contacted, 'school' : event.school, \
                'summary' : event.summary, 'student_id' : event.student_id, 'name_contacted' : event.name_contacted}
            elif request.method=='POST':
                return {'error' : 'Must fill out all required fields.'}
            else:              
                return render_template('event_boot.html', user=current_user, form=form, edit=True, task=task, event=event)
    except:
        return {'error' : 'An error occurred while editing this event.'}
        
@main_bp.route('/main/reports', methods=['GET', 'POST'])
@login_required
def reports():
        default=None
        script=None
        div=None
        employees=User.query.filter(User.id>0).order_by(User.last_name).all()
        schools=School.query.order_by(School.school_name).all()
        if request.method=='POST':
            school=request.form.get('school')
            employee=request.form.get('employee')
            if school:
                event_query=Event.query.filter_by(school=school).order_by(Event.complete_timestamp)
                df=pd.read_sql(event_query.statement, event_query.session.bind)
                df_group=df.groupby(['event_type']).agg({'event_type' : 'count'});
                df_group.columns=['count']
                df_group=df_group.reset_index()
                factors=df['event_type'].unique().tolist()
                q=figure(plot_height=350, title="Events in {}".format(school), toolbar_location="right",
                x_range=FactorRange(*factors))
                
                q.vbar(x='event_type', top='count', source=df_group, width=0.5)
                
                script, div = components(q)
        
                return render_template('report.html', default=default, user=current_user, employees=employees, schools=schools, script=script, div=div)
            elif employee:
                event_query=Event.query.filter_by(person_completed=employee).order_by(Event.complete_timestamp)
                df=pd.read_sql(event_query.statement, event_query.session.bind)
                df_group=df.groupby(['event_type']).agg({'event_type' : 'count'});
                df_group.columns=['count']
                df_group=df_group.reset_index()
                factors=df['event_type'].unique().tolist()
                employee_name=User.query.filter_by(employee_id=employee).first()
                q=figure(plot_height=350, title="Events by {}".format(employee_name.full_name), toolbar_location="right",
                x_range=FactorRange(*factors))
                
                q.vbar(x='event_type', top='count', source=df_group, width=0.5)
                
                script, div = components(q)
        
                return render_template('report.html', default=default, user=current_user, employees=employees, schools=schools, script=script, div=div)
            else:
                pass
                
                
        event_query=Event.query.order_by(Event.complete_timestamp)
        df=pd.read_sql(event_query.statement, event_query.session.bind)
        df_group=df.groupby(['event_type']).agg({'event_type' : 'count'});
        df_group.columns=['count']
        df_group=df_group.reset_index()
        df_group['color']=Category20c[df_group.shape[0]]
        df_group['angle']=df_group['count']/df_group['count'].sum()*2*pi
        df_group['percent']=np.round((df_group['count']/df_group['count'].sum()*100))
        
        
        p = figure(plot_height=350, title="Events in District", toolbar_location="right",
        tools="hover", tooltips="@event_type: @count events, @percent percent", x_range=(-1, 2.0))
        
        
        p.wedge(x=0.5, y=1, radius=0.75,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="green", fill_color='color', legend_field='event_type', source=df_group)
        
        '''df_group["percent"] = df_group['percent'].astype(str)
        df_group['percent'] = df_group['percent'].str.pad(35, side = "left")
        source=ColumnDataSource(df_group)
        labels = LabelSet(x=0.5, y=1, text='percent', text_align='center', text_color='white',
        angle=cumsum('angle', include_zero=True), source=source, render_mode='canvas')

        p.add_layout(labels)'''
        p.axis.axis_label=None
        p.axis.visible=False
        p.grid.grid_line_color = None
        
        script, div = components(p)
        
        return render_template('report.html', default=default, user=current_user, employees=employees, schools=schools, script=script, div=div)

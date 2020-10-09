# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 10:12:34 2019

@author: jpick
"""
import re, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil.relativedelta import relativedelta
from flask import render_template, flash, redirect, request, jsonify, json, make_response, send_file, send_from_directory, url_for
from flask import current_app as app
import pandas as pd
import numpy as np
from flask_login import current_user, login_user, login_required, logout_user
from .models import db, User
from . import login
from sqlalchemy import text, create_engine, and_, Date, DateTime, cast, or_, func
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, load_only
#from flask_sqlalchemy_session import flask_scoped_session
from werkzeug.urls import url_parse
from werkzeug.datastructures import TypeConversionDict
from flask_admin.contrib.sqla import ModelView

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',title='Home', user=current_user)


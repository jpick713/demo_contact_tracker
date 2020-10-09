# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 02:58:13 2020

@author: jpick
"""
from dotenv import load_dotenv
load_dotenv()
import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI= os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    #SQLALCHEMY_DATABASE_URI= os.environ.get('DATABASE_URL') or \
    #	'mssql+pyodbc://@Jamie'

    
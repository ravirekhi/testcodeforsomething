from functools import wraps
from flask import g, request, redirect, url_for,session
from app.config import db_config,s3_config
import mysql.connector
import boto3

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


def upload_to_s3(key,fileBytes):
    s3 = boto3.resource('s3')
    s3.Object(s3_config['bucket'], key).put(Body=fileBytes,ACL='public-read')




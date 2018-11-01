from flask import render_template, redirect, url_for,session
from app.utils import login_required

from app import webapp



@webapp.route('/',methods=['GET'])
@webapp.route('/index',methods=['GET'])
# Display an HTML page with links
def main():
    if 'username' in session:
        return redirect(url_for('welcome',user=session['username']))
    return render_template("index.html",title="ManagerUI for ECE1779 Assignment 1")






@webapp.route('/welcome', methods=['GET'])
@login_required
def welcome(user=""):
    return render_template("welcome.html", title="Welcome "+session['username'])


from flask import render_template, redirect, url_for, request, g,flash,session
from app import webapp
from app.utils import get_db

@webapp.route('/login',methods=['GET','POST'])
# Display an HTML page with links
def login():
    if request.method == 'GET':
        if 'username' in session and session['username'] == 'admin':
            return redirect(url_for('welcome'))
        return render_template("login.html",title="Log In")
    return redirect(url_for('validate_user',user=request.form['user']))



@webapp.route('/signup',methods=['GET','POST'])
# Display an HTML page with links
def signup():
    if(request.method == 'GET'):
        return render_template("signup.html",title="Sign up")
    cnx = get_db()
    cursor = cnx.cursor()
    username = request.form['user']
    password = request.form['psw']
    query = "SELECT 1 from users where login=%s"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    if row is not None:
        error_msg = "Error: Username already exists. Please choose a different username!"
        return render_template("signup.html", title="Sign up",
                           error_msg=error_msg)
    query = "INSERT INTO users (login,password) VALUES (%s,%s)"
    cursor.execute(query, (username, password))
    cnx.commit()
    flash("User created successfully!")
    return redirect(url_for('login'))
        #render_template("login.html", title="Log In")


@webapp.route('/login/validate',methods=['POST'])
# Display an HTML page with links
def validate_user():
    cnx = get_db()
    cursor = cnx.cursor()
    username = request.form.get('user')
    if username != 'admin':
        error_msg = "Authorization Error: Only Administrators are allowed to login!"
        return render_template("login.html", title="Log In",
                               error_msg=error_msg)
    password = request.form.get('psw')
    query = "SELECT id FROM users WHERE login=%s AND password=%s"
    cursor.execute(query,(username,password))
    row = cursor.fetchone()
    if row is None:
        error_msg = "Error: Username or Password is invalid!"
        return render_template("login.html", title="Log In",
                           error_msg=error_msg)
    session['username'] = username
    session['userid'] = row[0]
    print (session['userid'] )
    return redirect(url_for('welcome',user=username))
        #render_template("redirect.html", title="Log In")


@webapp.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('userid', None)
    session.pop('exp_thr', None)
    session.pop('shr_thr', None)
    session.pop('exp_rto', None)
    session.pop('shr_rto', None)
    session.pop('as_period', None)
    session.pop('as_counter', None)
    session.pop('cpu_period', None)
    return redirect(url_for('main'))
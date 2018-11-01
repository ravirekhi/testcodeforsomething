from flask import render_template, redirect, url_for, request,session
from app import webapp
import boto3
from app.utils import login_required,get_db
from flask.json import jsonify
import datetime

@webapp.route('/autoscaling', methods=['GET'])
@login_required
def view_as_plcy():
    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT * FROM aspolicy"
    cursor.execute(query)
    return render_template('autoscaling/list.html', title="Auto Scaling policy",cursor=cursor)



@webapp.route('/savenewpolicy', methods=['POST'])
# Create a new student and save them in the database.
def save_new_policy():
    exp_thr = request.form.get('exp_thr',type=int)
    shr_thr = request.form.get('shr_thr',type=int)
    exp_rto = request.form.get('exp_rto',type=int)
    shr_rto = request.form.get('shr_rto',type=int)
    as_period = request.form.get('as_period',type=int)
    as_counter = request.form.get('as_counter',type=int)

    error = False

    if exp_thr < 0 or exp_thr > 100 or \
                    shr_thr < 0 or shr_thr > 100 or \
                    shr_rto < 1 or \
                    exp_rto < 1 or \
                    as_period <= 0 or \
                    as_counter <= 0:
        error = True
        error_msg = "Error: One of the fields is invalid!"

    if error:
        return render_template("welcome.html", title="ManagerUI for ECE1779 Assignment 1", error_msg=error_msg)

    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' UPDATE aspolicy set
    parameter_val=%s where parameter_nm=%s
    '''
    cursor.execute(query, (exp_thr,'exp_thr'))
    cnx.commit()
    cursor.execute(query, (shr_thr,'shr_thr'))
    cnx.commit()
    cursor.execute(query, (shr_rto, 'shr_rto'))
    cnx.commit()
    cursor.execute(query, (exp_rto, 'exp_rto'))
    cnx.commit()
    cursor.execute(query, (as_period, 'as_period'))
    cnx.commit()
    cursor.execute(query, (as_counter, 'as_counter'))
    cnx.commit()
    return redirect(url_for('view_as_plcy'))


@webapp.route('/editPolicyStatus', methods=['GET'])
@login_required
def editPolicyStatus():
    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' UPDATE aspolicy set
        parameter_val=%s where parameter_nm=%s
        '''
    cursor.execute(query, (request.args.get('plcy_status',type=int), 'plcy_status'))
    cnx.commit()
    return jsonify(data="Policy has been saved successfully")

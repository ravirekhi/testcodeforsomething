from flask import render_template, redirect, url_for, request,session
from app import webapp
import boto3
from app.utils import login_required,get_db
from app.config import ec_config,s3_config
from flask.json import jsonify
import datetime



@webapp.route('/workers', methods=['GET'])
@login_required
def workers_list():
    if 'exp_thr' not in session:
        session['exp_thr'] = 100
    if 'shr_thr' not in session:
        session['shr_thr'] = 0
    if 'exp_rto' not in session:
        session['exp_rto'] = 1
    if 'shr_rto' not in session:
        session['shr_rto'] = 1
    if 'as_period' not in session:
        session['as_period'] = 30000
    if 'cpu_period' not in session:
        session['cpu_period'] = 60000
    if 'as_counter' not in session:
        session['as_counter'] = 5
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [ec_config['ami-id']]},{'Name':'instance-state-name','Values':['running','pending']},])
    for instance in instances:
        image=ec2.Image(instance.image_id)
        print(instance.id,instance.image_id,image.name,instance.state['Name'])
    return render_template('workers/list.html', title="Workers List",instances=instances)

@webapp.route('/updateIncidentStatus/<id>', methods=['POST'])
@login_required
def updateIncidentStatus(id):
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [ec_config['ami-id']]},
                                              {'Name': 'instance-state-name', 'Values': ['running', 'pending']}, ])
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-id', 'Values': [id]},])
    for instance in instances:
        return jsonify({'InstanceState' : instance.state['Name']})
    return "No new state"

@webapp.route('/getallCPUUtilization/<id>', methods=['POST'])
@login_required
def getallCPUUtilization(id):
    periods = [60,300,3600]
    client = boto3.client('cloudwatch')
    stats = []
    for period in periods:
        stats.append( client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': id
                },
            ],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=period+(period/2)),
            EndTime=datetime.datetime.utcnow(),
            Period=period,
            Statistics=[
                'SampleCount', 'Average', 'Minimum', 'Maximum',
            ],
        ))
    if len(stats) > 0:
        return  jsonify({'Datapoints': stats[0]},{'Datapoints': stats[1]},{'Datapoints': stats[2]})
    print("No new data")
    return "NoUpdate"


@webapp.route('/createInstance/', methods=['POST'])
@login_required
def createInstance():
    ec2 = boto3.resource('ec2')
    qty = request.form.get('qty',type=int)
    print(type(qty))
    ec2.create_instances(
        ImageId=ec_config['ami-id'],
        MinCount=1,
        MaxCount=qty,
        KeyName=ec_config['key_name'],
        SecurityGroups=[
            ec_config['secty_grp'],
        ],
        SecurityGroupIds=[
            ec_config['secty_grpId'],
        ],
        InstanceType=ec_config['instance_type'],
        Monitoring={
            'Enabled': True
        }
    )
    ids=[]
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [ec_config['ami-id']]},
                                              {'Name': 'instance-state-name', 'Values': ['running','pending']}, ])

    for instance in instances:
        ids.append({'InstanceId': instance.id})
    registerInstance(ids);
    return redirect(url_for('workers_list'))


def registerInstance(ids):
    client = boto3.client('elb')
    response = client.register_instances_with_load_balancer(
    LoadBalancerName=ec_config['loadbalancer_name'],
    Instances=ids,
    )


def deregisterInstance(ids):
    client = boto3.client('elb')
    response = client.deregister_instances_from_load_balancer(
    LoadBalancerName=ec_config['loadbalancer_name'],
    Instances=ids
    )

@webapp.route('/removeInstance/', methods=['POST'])
@login_required
def removeInstance():
    instances = []
    ids=request.form.getlist('selected')
    for id in ids:
        instances.append({'InstanceId': id})
    deregisterInstance(instances)
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=ids).stop()
    ec2.instances.filter(InstanceIds=ids).terminate()
    return redirect(url_for('workers_list'))

@webapp.route('/deleteData', methods=['GET'])
@login_required
def deleteData():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_config['bucket'])
    for key in bucket.objects.all():
        key.delete()
    query = "DELETE from images where  id>0"
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    query="ALTER TABLE images auto_increment=1"
    cursor.execute(query)
    cnx.commit()
    return redirect(url_for('welcome'))


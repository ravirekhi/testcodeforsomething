from functools import wraps

import mysql.connector
import boto3
import datetime
import math
import time

db_config = {'user': 'root',
             'password': 'ece1779pass',
             #'host': '34.206.92.95',
              'host':"172.31.46.122",
             'database': 'ece1779'}

s3_config = { 'bucket':'ece1779.a1.fk'
            }

ec_config = { 'ami-id' : 'ami-d04ffbc6',
              'key_name' : 'ece1779_a1_FK',
              'secty_grp' : 'launch-wizard-2',
              'secty_grpId' : 'sg-4c626930',
              'instance_type' : 't2.small',
              'loadbalancer_name': 'ece1779a1fkLoadBalancer'

            }


def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db =  connect_to_database()
    return db

shrCounter=0
expCounter=0

def registerInstance(ids):
    client = boto3.client('elb')
    response = client.register_instances_with_load_balancer(
    LoadBalancerName=ec_config['loadbalancer_name'],
    Instances=ids,
    )

def expInstance(qty):
    ec2 = boto3.resource('ec2')
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
    ids = []
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [ec_config['ami-id']]},
                                              {'Name': 'instance-state-name', 'Values': ['running', 'pending']}, ])

    for instance in instances:
        ids.append({'InstanceId': instance.id})
    registerInstance(ids)

def deregisterInstance(ids):
    client = boto3.client('elb')
    response = client.deregister_instances_from_load_balancer(
    LoadBalancerName=ec_config['loadbalancer_name'],
    Instances=ids
    )


def shrInstance(qty):
    ids = []
    ids2 = []
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [ec_config['ami-id']]},
                                              {'Name': 'instance-state-name', 'Values': ['running']}, ])
    count =0;
    for instance in instances:
        ids.append(instance.id)
        ids2.append({'InstanceId': instance.id})
        count+=1
        if count == qty:
            break

    deregisterInstance(ids2)
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=ids).stop()
    ec2.instances.filter(InstanceIds=ids).terminate()


def runAutoScaling(totalAvgCPU300,count):

    global shrCounter
    global expCounter
    if (float(totalAvgCPU300) > policy['exp_thr']):
        shrCounter=0;
        expCounter += 1;
        print("exp: ",expCounter)
        if(expCounter == policy['as_counter']):
            newQty = count * (policy['exp_rto']-1)
            if (newQty >= 1):
                expInstance(newQty);
                print("Expand by ",newQty)
            expCounter = 0

    elif (float(totalAvgCPU300) < policy['shr_thr']  and count > 1):
        shrCounter += 1
        expCounter = 0
        print("shr: ",shrCounter)
        if (shrCounter == policy['as_counter']):
            newCount = math.ceil(count / policy['shr_rto'])
            if (newCount != 0 and newCount < count):
                nRemove = count - newCount
                shrInstance(nRemove)
                print("remove ",nRemove)


            shrCounter = 0
    else:
        shrCounter = 0;
        expCounter = 0;



        return 0




ec2 = boto3.resource('ec2')
client = boto3.client('cloudwatch')





while True:
    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT * FROM aspolicy"
    cursor.execute(query)
    policy = {}
    for row in cursor:
        policy.update({row[1]: row[2]})
    print(policy)
    if (policy['plcy_status'] == 1):
        count = 0
        totalAvgCPU300 = 0
        validFlag = False
        instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [ec_config['ami-id']]},
                                                  {'Name': 'instance-state-name', 'Values': ['running']}, ])
        print("Entering for loop")
        for instance in instances:
            stats = client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance.id
                    },
                ],
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=120),
                EndTime=datetime.datetime.utcnow(),
                Period=120,
                Statistics=[
                    'SampleCount', 'Average', 'Minimum', 'Maximum',
                ],
            )

            if len(stats['Datapoints']) > 0:
                print(stats['Datapoints'])
                totalAvgCPU300=float(totalAvgCPU300)+stats['Datapoints'][0]['Average']
                count+=1
                validFlag = True
            else:
                print("no new data for ",instance.id)
                validFlag = False
                break
        if(validFlag):
            totalAvgCPU300=float(totalAvgCPU300)/count
            totalAvgCPU300 = "{0:.2f}".format(totalAvgCPU300)
            print(totalAvgCPU300)
            runAutoScaling(totalAvgCPU300,count)
        time.sleep(60)


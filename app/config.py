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


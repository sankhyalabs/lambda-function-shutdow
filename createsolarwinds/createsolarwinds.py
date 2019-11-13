import os
import boto3

init_script = """#!/bin/bash
service ntpd stop
date 100212122019
nohup /home/ec2-user/dpa/dpa_12_1_701/startup.sh &"""



ec2 = boto3.resource('ec2')


def lambda_handler(event, context):

    instance = ec2.create_instances(
        ImageId=os.environ['AMI'],
        InstanceType=os.environ['INSTANCE_TYPE'],
        KeyName=os.environ['KEY_NAME'],
        SubnetId=os.environ['SUBNET_ID'],
        SecurityGroupIds=[os.environ['SECURITY_GROUP_ID']],
        MaxCount=1,
        MinCount=1,
        UserData=init_script
    )

    print("New instance created:", instance[0].id)


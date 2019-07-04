#coding: utf-8
import boto3
import re
import datetime

ec = boto3.client('ec2')
iam = boto3.client('iam')

"""
Essa funçao verifica todos os snapshots que possuem a tag "DeleteOn" contendo o dia atual formatado como YYYY-MM-DDD.
"""

def lambda_handler(event, context):

    delete_on = datetime.date.today().strftime('%Y-%m-%d')

    filters = [
        {'Name': 'tag-key', 'Values': ['DeleteOn']},
        {'Name': 'tag-value', 'Values': [delete_on]},
    ]

    snapshot_response = ec.describe_snapshots(Filters=filters)

    if len(snapshot_response['Snapshots']) == 0:
        print "Don't have snapshots to be deleted"
    else:
        print "Found %d snapshots to be deleted" % len(snapshot_response['Snapshots'])

    for snap in snapshot_response['Snapshots']:
        print "Deleting snapshot %s" % snap['SnapshotId']
        ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
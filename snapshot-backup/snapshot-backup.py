#coding: utf-8

import boto3 # biblioteca da AWS para desenvolvimento em phyton.
import collections
import datetime

ec = boto3.client('ec2')

"""

Para que a instância seja mapeada para o snapshot automatico, deve ser adicionado as tags abaixo:
    1) Backup // indica que devemos fazer o backup da instância
    2) Retention // indica quantos dias de backup precisamos manter

"""
def lambda_handler(event, context):
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup']},
        ]
    ).get(
        'Reservations', []
    )

    instances = [
        i for r in reservations
        for i in r['Instances']
    ]

    print "Found %d instances that need backing up" % len(instances)

    to_tag = collections.defaultdict(list)


    for instance in instances:
        try:
            retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
        except IndexError:
            retention_days = 7

        try:
            name = [
                t.get('Value') for t in instance['Tags']
                if t['Key'] == 'Name'][0]
        except IndexError:
            name = "ec2"

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            print "Found EBS volume %s on instance %s" % (
                vol_id, instance['InstanceId'])

            snap = ec.create_snapshot(
                VolumeId=vol_id,
                Description="Snapshot of " + name + " generated automatically by lambda function",
            )

            to_tag[retention_days].append(snap['SnapshotId'])

            print "Retaining snapshot %s of volume %s from instance %s for %d days" % (
                snap['SnapshotId'],
                vol_id,
                instance['InstanceId'],
                retention_days,
            )


    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        print "Will delete %d snapshots on %s" % (len(to_tag[retention_days]), delete_fmt)
        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
            ]
        )
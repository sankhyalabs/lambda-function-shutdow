import boto3


def lambda_handler(event, context):
    region = 'sa-east-1'

    resource = boto3.resource('ec2')
    client = boto3.client('ec2', region_name=region)

    for instance in resource.instances.filter(Filters=[{'Name': 'tag:Reboot', 'Values': ['True', 'true']}]):
        resultado = instance.id
        client.reboot_instances(InstanceIds=[str(resultado)])
        print('Reboot Instance: ' + str(resultado))

import json
import boto3
import logging
import base64
import time

# request-spot-fleet
def handler(event, context):
    try:
        client = boto3.client('ec2')
        user_data = 'Hello world!'
        user_data_base64 = base64.b64encode(user_data.encode("utf-8")).decode("utf-8")
        launch_specifications = []
        instance_types = [ 
            'm6g.2xlarge',
            'm5.2xlarge',
            'm5a.2xlarge',
            'm5n.2xlarge',
            'm4.2xlarge',
            'r5.2xlarge',
            'r5d.2xlarge',
            'r5a.2xlarge',
            'r5n.2xlarge',
            'r4.2xlarge'
        ]
        #update the above instnace types you would like your spot fleet to choose from
        for type in instance_types:
            launch_template = {
                'SecurityGroups': [{'GroupId': 'sg-123456789abcdef'},], #update security group id
                'IamInstanceProfile': {'Name': 'AWSSpotInstanceProfile'}, #update/create an IAM Instance Profile and put the name here
                'ImageId': 'ami-exampleidhere', #update the ami-id for your instance
                'KeyName': 'key-pair-goes-here', #update the key-pair
                'InstanceType':type,
                'UserData': user_data_base64,
            }
            launch_specifications.append(launch_template)
        response = client.request_spot_fleet(
            SpotFleetRequestConfig={
                'AllocationStrategy': 'lowestPrice',
                'IamFleetRole': 'arn:aws:iam::ACCOUNTID:role/AWSRequestSpotFleetRole', #update/create an IAM Fleet Role and put the arn here
                'LaunchSpecifications': launch_specifications,
                'TargetCapacity': 1, #choose a target capacity
                'TerminateInstancesWithExpiration': True,
                'Type': 'maintain',
                'ReplaceUnhealthyInstances': True,
                'InstancePoolsToUseCount': 1,
            }
        )
        event['request_id'] = response['SpotFleetRequestId']
        event['request_id_found'] = True
        return event
    except Exception as e:
        print(e)
        event['request_id_found'] = False
        return event
    
# check-request-state
def handler1(event, context):
    try:
        client = boto3.client('ec2')
        print(event['request_id'])
        time.sleep(60)
        response = client.describe_spot_fleet_requests(
            SpotFleetRequestIds=[event['request_id']]
        )
        print(response)
        state = response['SpotFleetRequestConfigs'][0]['ActivityStatus']
        if state == 'fulfilled':
            event['request_succeeded'] = "true"
            return event
        if state == 'fulfilled':
            response2 = client.describe_spot_fleet_instances(
                SpotFleetRequestId='string'
            )
            event['instance_id'] = response2['ActiveInstances'][0]['InstanceId']
        elif state == 'pending_fulfillment':
            event['request_succeeded'] = "still_waiting"
            return event
        else:
            event['request_succeeded'] = "false"
            return event
    except Exception as e:
        print(e)
        event['request_succeeded'] = "failed"
        return event

# check-job-status
def handler2(event, context):
    client = boto3.client('dynamodb')
    response = client.get_item(
        TableName='new-company2', #update the table name here
        Key={
                'job_id' : {'S' : event['job_id']}
        },
        ProjectionExpression='job_status',
    )
    job_status = response['Item']['job_status']['S']
    if job_status == 'in_progress':
        event['job_completed'] = "in_progress"
        return event
    elif job_status == 'completed':
        event['job_completed'] = "true"
        return event
    else:
        event['job_completed'] = "false"
        return event
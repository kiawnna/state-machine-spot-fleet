import json
import boto3
import logging
import base64
import time

# request-spot-fleet
# This function requests a spot fleet with a target capacity of 1. A spot fleet is requested so that multiple instance types can
# be specified for spot to choose from.
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
# This function will continually check for the request_id of the spot fleet and return the appropriate status each time. If 
# an id is not found, the state machine will automatically have it check again after waiting for a set period of time
# until a request_id is found.
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
# This function will check the status of a job, job_status, stored in a DynamoDB table. Initially,
# a job_id needs to be passed into the execution, so this function knows which item to check in
# DynamoDB. An outside event (the job running on the instance--for this project a bash scrip
# was used to update the job_status to "completed" when the job was done running) needs to update
# the job_status, so that when a job is completed this function can return a completed status.
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
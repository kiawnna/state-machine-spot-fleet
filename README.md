# Basic Spot Instance Functions

This set of functions uses the Serverless framework to interact with Spot instances/Spot Fleet in AWS. These functions
are intended to be used with an AWS State Machine/ step funcitons. Once all is deployed, a State Machine will
1) request a spot fleet with a maxiumum of 1 instance, from the types specified in the function "request-spot-fleet",
2) check the request status multiple times until a request id is found, and 3) check the status of jobs being run
on the instnace via a table in DynamoDB (in this example, job data is stored initially in DynamoDB and updated as
needed, so the check-job-status function will check for an update to the specified column in DynamDB that corresponds
to the job status until it returns completed). It is meant to process batch jobs.


# Steps to Deploy
First update the serverless.yaml and handler.py files with custom parameters. You must create the EC2 Instance Profile
and IAM Fleet Role manually via IAM in the AWS UI. Use the command 'sls deploy' to deploy the python functions into
Lambda. Copy the arns from the functions into the state-machine-definition template where needed and then 
create a state machine with that code. You much pass a job_id into the execution manually.
=======
1) request a spot fleet with a maxiumum of 1 instance, from the types specified in the function request-spot-fleet,
2) check the request status multiple times until a request id is found, and
3) check the status of jobs being run on the instnace via a table in DynamoDB (in this example, job data is stored initially in DynamoDB and updated as needed, so the check-job-status function will check for an update to the specified column in DynamDB that corresponds to the job status until it returns completed).


# Steps to Deploy
Follow the below steps to get the entire project up and running in AWS. Eventually, a CloudFormation solution will be
provided, but currently familiarity with the AWS UI is needed. You will also need to have installed the Serverless framework
already.

# Step 1

Update the serverless.yaml file to contain your account-specific information. Update the handler.py file as needed.
Create and EC2 Instance Profile and IAM Fleet Role via IAM in AWS, then copy the name and/or arns into the handler.py file
where needed.

# Step 2
```
sls deploy
```
Run 'sls deploy' to deploy the Lambda functions into AWS.

# Step 3
Copy and paste the arns from the functions the Serverless framework created into the state-machine-definition.json file.

# Step 4
Create a State Machine with the state-machine-definition.json file and try to run an execution. You must pass in a job_id
into the execution. This will be updated to be autmated eventually.

Currently, the serverless.yaml file IS NOT set up with the least necessary IAM priveleges. It will be updated soon.

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
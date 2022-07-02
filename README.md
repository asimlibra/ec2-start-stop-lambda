# ec2-start-stop-lambda
Python Lambda function to start or stop EC2 instances based on a tag and send slack alerts
# Description
1. Launch Lambda function with python 3.8 runtime
2. Add tag with Key as `startstop` as value as `true` to the target EC2 instances you want to manage.
3. Create Cloudwatch Event rule (my usecase was a cron schedule), or if you want to call this lambda in any other way, pass this json as an input to the function 

    ```json
    {
      "Region": "us-west-1",
      "Action": "start"
    }
    ```

    - `Region`: region name that has the target EC2 instances
    - `Action` : "start" or "stop"

###IAM Permissions 
Create an IAM Policy with following JSON and attach to Lambda execution role. This allows lambda function to describe, start, and stop instances.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "StopStartEC2",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeRegions",
                "ec2:DescribeInstances",
                "ec2:StopInstances",
                "ec2:StartInstances"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

import json
import boto3
import traceback
import urllib3

webhook = "https://hooks.slack.com/services/XXXXXXX/XXXXXXX/XXXXXXXXX"

def slack_attachment_sting_from_list(instance_ids):
    attachment_string = ""
    for i in instance_ids:
        attachment_string = '- ' + i + ' \n' + attachment_string
    return attachment_string

def send_slack_message(action, instanceids):
    if action == 'invalid':
        slack_message = {
            'channel': "#infra-alerts",
            'text': "Could not stop or start instances, please investigate."
        }
    else:
        slack_message = {
            'channel': "#infra-alerts",
            'username': "EC2 Management Lambda",
            'icon_emoji': ":alarm_clock:",
            'text': "Following instances are going to *" + action + "*:"
            'attachments': [
                {
                    "fields": [
                        {"title": "Instance IDs", "value": slack_attachment_sting_from_list(instanceids), "short": "false"}
                    ]
                }
            ]
        }
    try:
        http = urllib3.PoolManager()
        response = http.request('POST',
                                webhook,
                                body = json.dumps(slack_message),
                                headers = {'Content-Type': 'application/json'},
                                retries = False)
    except:
        traceback.print_exc()

    return True

def lambda_handler(event, context):
  try:
    region = event['Region']
    action = event['Action']
    client = boto3.client('ec2', region)
    response = client.describe_instances(Filters=[{'Name': 'tag:startstop', "Values": ['true']}])

    target_instans_ids = []
    for reservation in response['Reservations']:
      for instance in reservation['Instances']:
        tag_name = ''
        for tag in instance['Tags']:
          if tag['Key'] == 'Name':
            tag_name = tag['Value']
            break

        target_instans_ids.append(instance['InstanceId'])

    if not target_instans_ids:
      print('No instances were found for automatic start / stop.')
    else:
      if action == 'start':
        client.start_instances(InstanceIds=target_instans_ids)
        print('started instances.')
      elif action == 'stop':
        client.stop_instances(InstanceIds=target_instans_ids)
        print('stopped instances.')
      else:
        print('Invalid action.')
        action = "invalid"
    send_slack_message(action, target_instans_ids)
    return {
      "statusCode": 200,
      "message": 'Finished automatic start / stop EC2 instances process and sent slack notification. [Region: {}, Action: {}]'.format(event['Region'], event['Action'])
    }
  except:
    print(traceback.format_exc())
    return {
      "statusCode": 500,
      "message": 'An error occured at automatic start / stop EC2 instances process.'
    }

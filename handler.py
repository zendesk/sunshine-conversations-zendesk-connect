import json, os, datetime, requests

print("Launching function...")

required_payload_fields = ["campaign_id"]
# Unused Connect values: ['id', 'user_id']
required_payload_data_fields = ["app_id", "integration_id", "destination_id", "msg_text"]

def parse_campaigns(envList):
    li = envList.split(",")
    for i in range(0, len(li)):
        li[i] = li[i].strip() 
    return li

def fail_unauthorised():
    response={
        "statusCode": 403,
        'body': "Unauthorised"
    }
    print(response)
    return response

def fail_badRequest():
    response={
        "statusCode": 400,
        'body': "Bad request"
    }
    print(response)
    return response

def receiveWebhook(event, context):
    print("\n\nReceived event @ %s:" % datetime.datetime.now())
    print('connectNotification() called:\nHeaders:\n\t"%s"\nBody:\n\t"%s"' % (event['headers'], event['body']))

    # Validation
    if "Authorization" not in event['headers'].keys():
        fail_badRequest()

    request_body = json.loads(event["body"])

    for key in required_payload_fields:
        if key not in request_body.keys():
            print("ERROR: Missing required field '%s'" % key)
            fail_badRequest()
    for key in required_payload_data_fields:
        if key not in request_body['data'].keys():
            print("ERROR: Missing required field 'data > %s'" % key)
            fail_badRequest()
    # TODO: Check for shorthand syntax in 'msg_text' (?)

    ##Auth
    if request_body['campaign_id'] not in parse_campaigns(os.environ['authorized_campaign_list']):
        fail_unauthorised()

    ## Hard-coded NotifyAPI values:
    storage = "full"
    msg_role = "appMaker"
    msg_type = "text"

    ## Required values event.data.{}
    appId = request_body['data']['app_id']
    integrationId = request_body['data']['integration_id'] #// i.e., WhatsApp Integration
    destinationId = request_body['data']['destination_id'] #// User- and Channel-specific id (externalId); set later
    msg_text = request_body['data']['msg_text']

    notify_endpoint = "https://api.smooch.io/v1/apps/%s/notifications" % appId
    notify_header = {
            'content-type': 'application/json',
            #'authorization': 'Bearer %s' % JWT
            'Authorization': event['headers']['Authorization']
    }
    notify_data = {
        "storage": storage,
        "destination": {
            "integrationId": integrationId,
            "destinationId": destinationId
        },
        # Standard Smooch-message structure
        "message": {
            "role": msg_role,
            "type": msg_type,
            "text": msg_text
        }
    }

    print("\nRequest url: %s" % notify_endpoint)
    print("Request header:\n\t%s" % notify_header)
    print("Request data:\n\t%s" % notify_data)

    notification_resp = requests.post(notify_endpoint, data=json.dumps(notify_data), headers=notify_header)

    print("\nResult:", notification_resp.status_code)
    print("Response body:", notification_resp.text)
    
    response = {
        "statusCode": notification_resp.status_code,
        'body': notification_resp.text
    }
    if response['statusCode'] != 201:
        print(locals())

    return response
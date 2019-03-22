import json, os, requests, datetime

print("Launching function...")

#env_vars=[ "SMOOCH_JWT", "SMOOCH_APPID", "SMOOCH_INTEGRATIONID" ]
WA_message_template = {
    # update below with your namespace/template/variables/fallback
    "fallbackText": "HSM Sent: Test message from Smooch",
    "WABA_namespace": "whatsapp:hsm:communications:smoochio",
    "template_name": "test_localized",
    # Template text: "Hi {{1}}, your {{2}} reservation is confirmed!"
    "variables": [
        "{appUserName}",
        # for this sample, appUserName remains as a variable for later substitution, once the userName is known
        "Casa Geranio"
    ]
}

notify_endpoint="https://api.smooch.io/v1/apps/%s/notifications" % os.environ['SMOOCH_APPID']
notify_header = {
        'content-type': 'application/json',
        'authorization': 'Bearer %s' % os.environ['SMOOCH_JWT']
}
notify_data = {
    "storage": "full",
    "destination": {
        "integrationId": os.environ["SMOOCH_INTEGRATIONID"], #// i.e., WhatsApp Integration
        "destinationId": "{targetPhone}" #// User- and Channel-specific id (externalId); set later
    },
    # Standard Smooch-message structure
    "message": {
        "role": "appMaker",
        "type": "text",
        "text": "&[{fallback}]({namespace}, {template}{vars})".format(
            fallback = WA_message_template['fallbackText'],
            namespace = WA_message_template['WABA_namespace'],
            template = WA_message_template['template_name'],
            vars = ", " + ', '.join(map(str, WA_message_template["variables"])) if len(WA_message_template["variables"]) > 0 else ""
        )
    }
}

def connectNotification(event, context):
    print("\n\nReceived event @ %s:" % datetime.datetime.now())
    print('connectNotification() called:\nHeaders:\n\t"%s"\nBody: "%s"' % (event['headers'], event['body']))
    
    # TODO: Auth reqests via `User-defined Header`; e.g.:
    '''
    if 'CONNECT_AUTHHEADER' in os.environ and 'CONNECT_AUTHKEY' in os.environ:
        if event['headers'][os.environ['CONNECT_AUTHHEADER']] != os.environ['CONNECT_AUTHKEY']:
            response={
                "statusCode": 403,
                'body': "Unauthorised"
            }
            return response
    '''
    
    request_body = json.loads(event["body"])
    if 'contactName' in request_body['data'].keys():
        contactName = request_body['data']['contactName']
    else:   # instead of 'hello <name>', use 'hello there'
        contactName = 'there'
    
    # set destinationId = userPhone
    notify_data["destination"]["destinationId"] = request_body['data']['target']
    # update userName as variable in HSM shorthand
    notify_data["message"]['text'] = notify_data["message"]['text'].format(appUserName=contactName) 
    
    print("\nRequest url: %s" % notify_endpoint)
    print("Request header:\n\t%s" % notify_header)
    print("Request data:\n\t%s" % notify_data)

    notification_resp = requests.post(notify_endpoint, data=json.dumps(notify_data), headers=notify_header)

    print("\nResult:", notification_resp.status_code)
    print("Response body:", notification_resp.text)

    response={
        "statusCode": notification_resp.status_code,
        'body': notification_resp.text
    }
    if response['statusCode'] != 201:
        print(locals())
    return response

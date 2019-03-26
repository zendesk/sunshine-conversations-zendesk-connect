# Deploying to Lambda with Serverless
## Pre-Requisites
1. Serverless (& Python-requirement package): `npm install -g serverless serverless-python-requirements`
2. Authorised/configured AWS IAM user (e.g.:)
    * keyId/secret under [serverless] in ~/.aws/credentials, or
    * `serverless config credentials --provider aws --key xxxxxxxxxxx --secret xxxxxxxxxxx`
3. Python3 (+ pip)
4. Zendesk Connect account
5. Smooch account & app, with:
    * Active WA ApiClient, and
    * Notification API access
6. Optional components
    * Zendesk Support account
    * Zendesk Integration on Smooch app
## Push environment variables to AWS (SSM)
Use the command `aws ssm put-parameter --name supermanToken --type String --value mySupermanToken`
### Required keys
* appId
* integrationId
* smoochJWT

NOTE: the JWT should be app-scoped
### Optional keys
Incoming request authentication is not implemented, but an example would be to use 2 additional SSM keys:
* connectAuthKey
* connectAuthSecret

NOTE: Serverless will raise a warning if keys are specified (serverless.yml) but not found in the AWS SSM/environment
## Clone smooch-zendesk-connect code
Clone this project
## Deploy to AWS Lambda with Serverless
`serverless deploy` (or `sls deploy`)

## Monitoring logs with Serverless
`serverless logs -f connect -t`
* `-f` specifies the Serverless function name
* `-t` to display/update logs in [near] real-time

# Create/configure a Zendesk Connect campaign
Configure a Variant of type 'Webhook':
* Endpoint: Use the value from the output of `sls deploy` (look for `endpoints:` and `POST - `)
* Authentication: None (Proof of concept only: authentication not included - shared-key use recommended for production use)
* Body: {
    "contactName": {{ 'first_name' | UserAttribute }} {{ 'last_name' | UserAttribute }},
    "target": {{ 'phone_number' | UserAttribute }}
}

NOTE: "cotactName" User name will be included in outgoing messages (for the example in this repo)
NOTE: for best results, "target" phone number should include '+' and country-code

# Trigger event(s)/launch broadcast from Zendesk Connect
As part of a broadcast campaign/Configure the trigger

# Looping replies back into Zendesk Support
* Connect the Smooch Marketplace _Zendesk integration_ to your smooch app: https://app.smooch.io/integrations/zendesk
* When users reply, a new ticket will be created, including the context of the last (up to 10) messages/notifications
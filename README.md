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
* connectCampaignIds

NOTE: Serverless will raise a warning if keys are specified (serverless.yml) but not found in the AWS SSM/environment
NOTE: _connectCampaignIds_ can contain a comma-separated list of authorised CampaignIds
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
* Authentication:
  * Type: User-defined Header
  * Key: `Authorization`
  * Value: `Bearer <app-scope Smooch JWT>`
  
NOTE: The function will also validate the campaign_id is whitelisted
* Body:
  * app_id: `<Smooch appId>`
  * integration_id: `<Smooch integrationId (for the desired channel)>`
  * destination_id: `<channel-specific Id for the user>`
  * msg_text: `<content of the message to be sent>`
  
NOTE: for SMS/WhatsApp, destinationId would be the phone number, with '+' and country-code
NOTE: To send a message based on a WhatsApp Message Template, please use HSM Shorthand: https://docs.smooch.io/guide/whatsapp#shorthand-syntax

# Update the campaignId whitelist
## Write the campaignId whitelist
Use the command `aws ssm put-parameter --name connectCampaignIdList --type String --value <list>` to update the Lambda environment.
<List> should be a comma-separated list of allowed Connect campaignIds
NOTE: Writing a single campaignId will overwrite any previous values.
## Read the campaignId whitelist
To get the current whitelist in order to append a new Campaign to the whitelist without squashing previously allowed campaignsUse the command `aws ssm put-parameter --name connectCampaignIdList`.
The current whitelist is shown as Parameter > Value > ""
## Update the campaignId whitelist
include the `--overwrite` argument in the command to replace the current value

# Ready for Trigger event(s)/Broadcast send from Zendesk Connect
For Broadcast campaigns, you can try a _Test Send_ or use _Final Send_.

# Looping replies back into Zendesk Support
1. Visit the Smooch Marketplace and add the _Zendesk integration_ to your smooch app: https://app.smooch.io/integrations/zendesk
    When users reply, a new ticket will be created, including the context of the last (up to 10) messages/notifications
2. Use the builtin Channel connector included with your Zendesk Support account
    When users reply, a new ticket will be created, including the context of notifications sent since the last user message

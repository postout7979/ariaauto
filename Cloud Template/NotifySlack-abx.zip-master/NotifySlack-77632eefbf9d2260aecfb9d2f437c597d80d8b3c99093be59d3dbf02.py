import json
import requests

def handler(context, inputs):
    webhook_url = context.getSecret(inputs["SlackWebhook"])
    #uncomment bellow line to troubleshoot webhook URL
    #print("Slack Webhook URL found: " + webhook_url)
    # get inputs from the deployment payload
    abx_owner = inputs["deploymentOwner"]
    abx_deploy = inputs["deploymentName"]
    abx_desc = inputs["description"]
    abx_action = inputs["eventType"]
    abx_status = inputs["status"]
    abx_msg = inputs["failureMessage"]
    # Set messagen based if the deploymnet was a creation or destruction
    if abx_action == "CREATE_DEPLOYMENT" : 
      if abx_status == "FAILED" :
        mytext = "WARNING: the deployment " + abx_deploy + " failed: " + abx_msg
      else :
        mytext = "A new resources has just been provisioned sucessfully called: " + abx_deploy + " and the requester is: " + abx_owner + " with the justification of: " + abx_desc
    elif abx_action == "DESTROY_DEPLOYMENT" :
      mytext = "The deployment called: " + abx_deploy + " has just been deleted by: " + abx_owner
    else :
      mytext = "Ops something went wrong with deployment: " + abx_deploy + " because of: " + abx_action + " better to check it out"
    slack_data = {'text': mytext}
    response = requests.post(webhook_url, data = json.dumps(slack_data), headers = {'Content-Type': 'application/json'})
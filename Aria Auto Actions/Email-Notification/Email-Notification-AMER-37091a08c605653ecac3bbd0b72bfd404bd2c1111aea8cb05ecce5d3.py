#-----------------------------------------------------------------------#
#                                                                       #
# ABX + EBS for e-mail notification (HTML and TXT) for vRA 8.X | Cloud  #
# https://blogs.vmware.com/management                                   #
# Author: Francisco Hernandez - hernandezf@vmware.com | @moffzilla      #
# (With Libraries and Code by VMware Technical Marketing Team)          #
# License: Apache License, Version 2.0                                  #
# Git: https://gitlab.com/moffzilla/vhermes.git                         #
# Version: 0.0.4.1                                                        #
#-----------------------------------------------------------------------#

import json
import base64
import requests
import time
import os
import traceback
import urllib3
urllib3.disable_warnings()
import smtplib 
import ssl
from socket import gaierror
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from json2html import *

def vra_get_token(url):
    api_url = '{0}csp/gateway/am/api/login?access_token'.format(url)
    headers= {'Content-Type': 'application/json'}
    data =  {
              "username":"configuser",
              "password": "VMware1!"
            }
    response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        #key = json_data['access_token']
        key = json_data['refresh_token']
        return key
    else:
        print(response.status_code)
        return None

def encoder(creds):
    message = creds
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def get_locker_password_ids(lcm_url_base,name,encoded_creds):
    api_url = '{0}lcm/locker/api/passwords/search'.format(lcm_url_base)
    headers = {'Content-Type': 'application/json','Authorization': 'Basic ' + encoded_creds,'accept': 'application/json'}
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        n = 0
        end_n = json_data['total']
        end_n = end_n - 1
        while True:
            pass_name = json_data['passwords'][n]['alias']
            if pass_name == name:
                print("Found Password")
                vmid = json_data['passwords'][n]['vmid']
                return vmid
                break
            elif n < end_n:
                n = n + 1
            elif n >= end_n:
                print("Did Not Find Password")
                break
    else:
        return response.status_code

def get_locker_password(lcm_url_base,vmid,lcm_pass,encoded_creds):
    api_url = '{0}lcm/locker/api/passwords/view/{1}'.format(lcm_url_base,vmid)
    data =  {
            	"rootPassword": lcm_pass
            }
    headers = {'Content-Type': 'application/json','Authorization': 'Basic ' + encoded_creds,'accept': 'application/json'}
    response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        strpass = json_data['password']
        return strpass
        print('Successfully Got Password')
    else:
        return None

def get_locker_username(lcm_url_base,name,encoded_creds):
    api_url = '{0}lcm/locker/api/passwords/search'.format(lcm_url_base)
    headers = {'Content-Type': 'application/json','Authorization': 'Basic ' + encoded_creds,'accept': 'application/json'}
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        n = 0
        end_n = json_data['total']
        end_n = end_n - 1
        while True:
            pass_name = json_data['passwords'][n]['alias']
            if pass_name == name:
                print("Found Locker Credentials and User Name")
                user_name = json_data['passwords'][n]['userName']
                return user_name
                break
            elif n < end_n:
                n = n + 1
            elif n >= end_n:
                print("Did Not Find Locker Credentials")
                break
    else:
        return response.status_code


def handler(context, inputs):
    
    outputs = {}
    ######## LCM Variables #####################
    lcm_url = "cava-r-96-020.eng.vmware.com"  # vRSLCM URL
    url = "https://" + lcm_url + "/"
    lcm_email_PasswordIdentifier = "smtpPassword" # vRSLCM Locker Alias for SMTP Password
    lcm_refreshToken_PasswordIdentifier = "vraRefreshToken" # vRSLCM Locker Alias for vRA Token
    lcm_pass = "VMware1!" # Password to access vRSLCM
    lcm_user = "admin@local" # Login to access vRSLCM
    cred = lcm_user + ":" + lcm_pass
    encoded_creds = encoder(cred)
    lcm_on = "off" # Set "on" to enable using vRSLCM or "off" to use local variables and replacing by "localsmtpPassword" & "localvraRefreshToken"
    localsmtpPassword = "A$CaB2b3@4c#" # paste your password
    #localvraRefreshToken = "0CPUkoLj6dcDCXm19OMEWs1uDPV4Z5im" # paste your vRA Token

    ######## SMTP Configuration START #####################
    smtp_port = 587 
    smtp_server = "smtp.office365.com" # FQDN for SMTP
    smtp_login = "fielddemo@vmware.com" # Login to access SMTP Server 
    sender_email = "fielddemo@vmware.com" # Email Address for Sender
    
    ######## vRA Configuration START #####################
    vraUrl = 'vra8-fielddemo.cmbu.local' # vRA on-prem URL
    vraAlias = 'Fielddemo AMER' # vRA or vRAC Alias
    vraCloud = "off" # "on" for using vRAC Cloud | "off" for using vRA on-prem
    
    if vraCloud == "on":
        vraUrl = 'api.mgmt.cloud.vmware.com'
        vracps = 'console.cloud.vmware.com'
    else:
        vracps = vraUrl
        
    ######## Variables END #####################
    print('Getting vRA Token')
    api_url_base = "https://" + vraUrl + "/"
    localvraRefreshToken = vra_get_token(api_url_base)


    ######## Fetch Email and vRA Credentials & Token from vRSLCM if lcm_on = yes #####################
    if lcm_on == "on":
        print('Getting User Name from Locker')
        username = get_locker_username(url,lcm_email_PasswordIdentifier,encoded_creds)
        
        print('Getting Email Credentials from Locker')
        vmid = get_locker_password_ids(url,lcm_email_PasswordIdentifier,encoded_creds)
        myEmailPassword = get_locker_password(url,vmid,lcm_pass,encoded_creds)
        
        print('Getting vRA Token from Locker')
        vmid = get_locker_password_ids(url,lcm_refreshToken_PasswordIdentifier,encoded_creds)
        myRefreshToken = get_locker_password(url,vmid,lcm_pass,encoded_creds)

        smtp_password = myEmailPassword
        vraRefreshToken = myRefreshToken 
    else:
        smtp_password = localsmtpPassword
        vraRefreshToken = localvraRefreshToken

    eventType = inputs["eventType"]
    status = inputs["status"]
    projectName = inputs["projectName"]
    requestType = inputs["requestType"]
    deploymentId = inputs['deploymentId'] 
    userName = inputs["__metadata"]["userName"]
    orgId = inputs["__metadata"]["orgId"]

    
    # Generate Bearer Token
    print('Generating Bearer Token...')    
    body = {
     "refreshToken": vraRefreshToken
    }

    response_bearerToken = requests.post('https://' + vraUrl + '/iaas/api/login?apiVersion=2019-01-15', data=json.dumps(body), verify=False)
    if response_bearerToken.status_code == 200:
        vraBearerToken = response_bearerToken.json()['token']
        bearer = "Bearer "
        bearer = bearer + vraBearerToken
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response_bearerToken.status_code, response_bearerToken.content))

    # Discovering Deployment Name and Resources Details
    print('Discovering Deployment Name...') 
    headers = {"Accept":"application/json","Content-Type":"application/json", "Authorization":bearer }
    response_deploymentName = requests.get('https://' + vraUrl + '/deployment/api/deployments/' + deploymentId + '?expandProject=true&expandResources=true&apiVersion=2019-01-15', data='', headers=headers, verify=False)
    if response_deploymentName.status_code == 200:
        myDeploymentName = response_deploymentName.json()['name']
        deploymentCreated = response_deploymentName.json()['createdAt']
        myResources_JSON = response_deploymentName.json()
        
    # Validate Expire dates
        if 'leaseExpireAt' in response_deploymentName.json():
            deploymentLease = response_deploymentName.json()['leaseExpireAt']
        else: 
            deploymentLease = 'Unlimited'
            
    # Detect Deployment Status and Event Type
        if status == "FINISHED":
            if eventType == "DESTROY_DEPLOYMENT":
                myResources_HTML = '<p>Resource Removed</p>'
                myResources_TXT = 'Status: Removed'
            else:
                myResources_HTML = json2html.convert(json = myResources_JSON)
                myResources_TXT = ''
        else:
                myResources_HTML = '<p style="color:red"><strong>OPERATION FAILED</strong></p>'
                myResources_TXT = 'Status: OPERATION FAILED'

    # write the HTML Template
        html = f"""\
        <html>
          <body>
            <p>Hi,<br><br>
            Thank you for your {requestType.lower()} {eventType.lower()} from <strong>{projectName}</strong>!</p>
            <p> Deployment name: <strong> {myDeploymentName} </strong></p>
            <p> Created at : <strong>{deploymentCreated}</strong></p>
            <p> Lease Expires: <strong>{deploymentLease}</strong></p>
        
            <h2><strong>Information:</strong></h2>
            <ul>   
            <li> Thank you for using vRA Automation Services</a> </li>
            <li> For more information <a href="https://{vraUrl}/">{vraAlias}</a></li>
            </ul> 
            <h2><strong>Resource Details:</strong></h2>
            {myResources_HTML}
          </body>
        </html>
        """
        
    # write the plain text Template
        text = f"""\
        Hi,
        Thank you for your {requestType.lower()} {eventType.lower()} from from {projectName}!
        Deployment name: {myDeploymentName}
        Created at : {deploymentCreated}
        Lease Expires: {deploymentLease}
        {myResources_TXT}
        For more information: https://{vraUrl}/
        """
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response_deploymentName.status_code, response_deploymentName.content))

    # Discovering Subscriber Email
    print('Discovering Subscriber Email...')
    headers = {"Accept":"application/json","Content-Type":"application/json", "Authorization":bearer }
    response_Email = requests.get('https://' + vracps + '/csp/gateway/am/api/users/' + userName + '/orgs/' + orgId + '/info?apiVersion=2019-01-15', data='', headers=headers, verify=False)
    if response_Email.status_code == 200:
        myEmail = response_Email.json()['user']['email']
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response_Email.status_code, response_Email.content)) 

    ######### Send Email Notification ########

    #Define Emailt Headers
    message = MIMEMultipart("alternative")
    message["Subject"] = f"vRA {requestType.lower()} {eventType.lower()} notification for {myDeploymentName} "
    message["From"] = sender_email
    message["To"] = myEmail
    
    # convert both parts to MIMEText objects and add them to the MIMEMultipart message
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # send email message
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo            
            server.login(smtp_login, smtp_password)
            server.sendmail(
                sender_email, myEmail, message.as_string()
        )
            server.close()
    
    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to the server. Bad connection settings?')
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to the server. Wrong user/password?')
    except smtplib.SMTPException as e:
        print('SMTP error occurred: ' + str(e))
    except smtplib.SMTPAuthenticationError as e:
        print('SMTP Authentication error: ' + str(e))
    except smtplib.SMTPSenderRefused as e:
        print('Sender address refused: ' + str(e))   
    except smtplib.SMTPRecipientsRefused as e:
        print('Recipient addresses refused: ' + str(e))       
    
    # Report if your message was sent or which errors need to be fixed 
    print('Sent Deployment information...')

    outputs = {
        "DeploymentName": myDeploymentName,
        "Email": myEmail,
        "requestType": requestType,
        "projectName": projectName,
        "deploymentCreated": deploymentCreated
    }

    return outputs    


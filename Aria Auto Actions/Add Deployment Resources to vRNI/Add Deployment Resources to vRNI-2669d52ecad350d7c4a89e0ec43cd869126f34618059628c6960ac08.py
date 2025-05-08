import json
import requests
import time
import os
import traceback
import urllib3
import urllib.parse
urllib3.disable_warnings()

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []
    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    results = extract(obj, arr, key)
    return results
        
def vrni_get_token(vrni_url):
    api_url = '{0}auth/token'.format(vrni_url)
    headers = {'Content-Type': 'application/json'}
    data =  {
                "username": "apiuser@local.com",
                "password": "VMware1!",
                "domain": {
                    "domain_type": "LOCAL"
                }
            }
    response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        key = json_data['token']
        return key
    else:
        print(response.status_code)
        return response.status_code

def create_vrni_app(vrni_url,vra_deployment,vrni_token):
    api_url = '{0}groups/applications'.format(vrni_url)
    headers = {'Content-Type': 'application/json','Authorization': 'NetworkInsight ' + vrni_token}
    data = {
             "name": vra_deployment
           }
    response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 201:
        json_data = json.loads(response.content.decode('utf-8'))
        resource_name = json_data['entity_id']
        return resource_name
    else:
        return response.status_code

def create_vrni_app_tier(vrni_url,vrni_app_id,vm_name,vrni_token):
    api_url = '{0}groups/applications/{1}/tiers'.format(vrni_url,vrni_app_id)
    headers = {'Content-Type': 'application/json','Authorization': 'NetworkInsight ' + vrni_token}
    data = {
                "name": vm_name,
                "group_membership_criteria": [
                    {
                        "membership_type": "SearchMembershipCriteria",
                        "search_membership_criteria": {
                            "entity_type": "VirtualMachine",
                            "filter": "Name = " + vm_name
                        }
                    }
                ]
            }
    response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 201:
        json_data = json.loads(response.content.decode('utf-8'))
        print("Members Added to vRNI App")
    else:
        print(response.status_code)
        return response.status_code
        
def get_vrni_app_ids(vrni_url,vrni_token):
    api_url = '{0}groups/applications'.format(vrni_url)
    headers = {'Content-Type': 'application/json','Authorization': 'NetworkInsight ' + vrni_token}
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        app_ids = extract_values(json_data,'entity_id')
        return app_ids
    else:
        return response.status_code

def get_vrni_app_names(vrni_url,vrni_token,vra_deployment):
    app_ids = get_vrni_app_ids(vrni_url,vrni_token)
    for i in app_ids:
        api_url = '{0}groups/applications/{1}'.format(vrni_url,i)
        headers = {'Content-Type': 'application/json','Authorization': 'NetworkInsight ' + vrni_token}
        response = requests.get(api_url, headers=headers, verify=False)
        if response.status_code == 200:
            json_data = json.loads(response.content.decode('utf-8'))
            app_name = json_data['name']
            if app_name == vra_deployment:
                return i
        else:
            print(response.status_code)
            return response.status_code

def delete_token(vrni_url,vrni_token):
    api_url = '{0}auth/token'.format(vrni_url)
    headers = {'Content-Type': 'application/json','Authorization': 'NetworkInsight ' + vrni_token}
    response = requests.delete(api_url, headers=headers, verify=False)
    if response.status_code == 204:
        print('Token Deleted')
    else:
        print(response.status_code)
        return response.status_code
    
def handler(context, inputs):
    print('Creating Application in vRNI from vRA')
    vrni_fqdn = inputs['vrni_fqdn']
    vm_name = inputs["resourceNames"][0]
    vra_deployment = inputs["customProperties"]['depName']
    vrni_url = "https://" + vrni_fqdn + "/api/ni/"
    vrni_token = vrni_get_token(vrni_url)
    vrni_app_exists = get_vrni_app_names(vrni_url,vrni_token,vra_deployment)
    if vrni_app_exists != None:
        print("Adding Members to vRNI App")
        create_vrni_app_tier(vrni_url,vrni_app_exists,vm_name,vrni_token)
        delete_token(vrni_url,vrni_token)
    else:
        print("Creating vRNI Application")
        vrni_app_id = create_vrni_app(vrni_url,vra_deployment,vrni_token)
        print("Adding Members to vRNI App")
        create_vrni_app_tier(vrni_url,vrni_app_id,vm_name,vrni_token)
        delete_token(vrni_url,vrni_token)

import os

import requests
import json

from client_examples.config import IMPROVISER_HOST
default_headers = {'content-type': 'application/json'}

r = requests.post(IMPROVISER_HOST + '/login',
                  data=json.dumps({'email': 'acidjunk@gmail.com', 'password': os.getenv("IMPROVISER_PASSWORD")}),
                  headers=default_headers)

response = r.json()
token = response['response']['user']['authentication_token']   #set token value
user_id = response['response']['user']['id']   #set token value
print(f'Received token: {token}, user_id: {user_id}')
auth_headers = {**default_headers, "Authentication-Token": token}

r = requests.get(IMPROVISER_HOST + f'/v1/users/current-user', headers=auth_headers)
response = r.json()
print(f"Userinfo + user prefs: {response}")
quick_auth_headers = {**default_headers, "Quick-Authentication-Token": f"{user_id}:{response['quick_token']}"}

# test getting and putting user prefs
r = requests.get(IMPROVISER_HOST + f'/v1/users/preferences', headers=quick_auth_headers)
response = r.json()
print(f"Got user preferences: {response}")

# test updating prefs
print("Testing update of language:")
payload = {"language": "nl"}
r = requests.patch(IMPROVISER_HOST + f'/v1/users/preferences', headers=quick_auth_headers, json=payload)
if not r.status_code == 200:
    print(r.__dict__)
else:
    print("OK")

print("Testing update of instrument_id")
payload = {"instrument_id": "b96ae0e8-aae8-484b-ab70-6d2f6fa2bc01"}
r = requests.patch(IMPROVISER_HOST + f'/v1/users/preferences', headers=quick_auth_headers, json=payload)
if not r.status_code == 200:
    print(r.__dict__)
else:
    print("OK")
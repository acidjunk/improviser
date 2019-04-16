"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.

It has a check that ensures that only one instance can be running at the same time.

Note: for now python 3.4 compatible.
"""
import json
import os

import requests

from render_new_riffs import retrieve_metadata, ENDPOINT_RIFFS, IMPROVISER_HOST


default_headers = {'content-type': 'application/json'}

r = requests.post(IMPROVISER_HOST + '/login',
                  data=json.dumps({'email': os.getenv("API_USER"), 'password': os.getenv("API_PASS")}),
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

# Retrieve riff id's:
# response = requests.get(ENDPOINT_RIFFS+'?range=0,299', headers=quick_auth_headers)
# print(len(response.json()))
# riff_ids = [riff["id"] for riff in response.json()]
riff_ids = ["e0493133-ce73-4cbe-9084-0b503893493b", "e0cbc581-d05e-4a6c-a6dd-487dc6dff91f", "4a51df6a-5d2a-44f8-896b-fd6826307a71"]

# print("Starting metadata extraction\n**************")
retrieve_metadata(riff_ids, auth_headers, skip_update=True)

# drawing = parse_svg_path('rendered/svg/riff_e0cbc581-d05e-4a6c-a6dd-487dc6dff91f_fis.svg')

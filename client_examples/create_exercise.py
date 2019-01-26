# Generate broken chord for M7, m7 en Dominant 7 chords in such a way that you get riffs that start on each chord note to ensure maximum instrument efficency
import sys

import json
import os

import requests

from client_examples.config import IMPROVISER_HOST

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')

if not API_USER or not API_PASS:
    sys.exit('Please set needed environment vars.')


def login():
    default_headers = {'content-type': 'application/json'}
    response = requests.post(IMPROVISER_HOST + '/login',
                             data=json.dumps({'email': API_USER, 'password': API_PASS}),
                             headers=default_headers).json()
    token = response['response']['user']['authentication_token']  # set token value
    user_id = response['response']['user']['id']
    auth_headers = {**default_headers, "Authentication-Token": token}
    print("Auth header initialised")
    response = requests.get(IMPROVISER_HOST + '/v1/users/current-user', headers=auth_headers).json()
    quick_auth_headers = {**default_headers, "Quick-Authentication-Token": f"{user_id}:{response['quick_token']}"}
    print("Quick auth header initialised")
    return auth_headers, quick_auth_headers


auth_headers, quick_auth_headers = login()

payload = {
    "name": "Bye, Bye, Black Bird",
    "description": "Good stuff",
    "root_key": "c",
    "is_public": False
}
response = requests.post(f"{IMPROVISER_HOST}/v1/exercises/", json=payload, headers=quick_auth_headers)
if response.status_code not in [200, 201, 204]:
    print(f"Error while creating exercise. Status: {response.status_code} with content: {response.content}")
else:
    print(f"Added exercise, with response {response.json()}")
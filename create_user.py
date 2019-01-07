import os
import uuid

import requests
import json

r = requests.post('http://localhost:5000/register',
                  data=json.dumps({'email': f'rene+{uuid.uuid4()}@formatics.nl',
                                   'username': 'test_user',
                                   'password': 'test_password',
                                   'first_name': 'Test',
                                   'last_name': 'User',
                                   'mail_announcements': True,
                                   'mail_offers': False}),
                  headers={'content-type': 'application/json'})
response = r.json()
print(response)  # check response
token = response['response']['user']['authentication_token']   #set token value

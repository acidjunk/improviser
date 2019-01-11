import os

import requests
import json

r = requests.post('https://api.improviser.education/login',
                  data=json.dumps({'email': 'acidjunk@gmail.com', 'password': os.getenv("IMPROVISER_PASSWORD")}),
                  headers={'content-type': 'application/json'})
response = r.json()
print(response)  # check response
token = response['response']['user']['authentication_token']   #set token value

#Now you can do authorised calls
r = requests.get('http://localhost:5000/v1/riffs', headers={'Authentication-Token': token})
print(r.status_code, r.json())

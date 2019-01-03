import requests
import json

r = requests.post('http://localhost:5000/v1/users/login',
                  data=json.dumps({'email': 'john@smit.com', 'password': '1234'}),
                  headers={'content-type': 'application/json'})
response = r.json()
print(response)  # check response
token = response['response']['user']['authentication_token']   #set token value

#Now you can do authorised calls
r = requests.get('http://localhost:5000/v1/riffs', headers={'Authentication-Token': token})
print(r.status_code, r.json())

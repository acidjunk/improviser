"""
Create an exercise via the REST endpoint
"""
import sys

import json
import os

import requests
import uuid

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

exercise_id = str(uuid.uuid4())

payload = {
    "id": exercise_id,
    "name": "Test" + exercise_id,
    "description": "Good stuff testing 2-5-1 chords",
    "root_key": "c",
    "is_public": False,
    "exercise_items": [
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 0,
            "riff_id": "61c290ec-9734-4364-b2ad-abf0b8ead3c2",
            "chord_info": "blaat",
         },
         {
            "pitch": "c",
            "octave": 0,
            "order_number": 1,
            "riff_id": "3ef38750-f5d4-49c9-a422-aa01dfb8bb58",
         },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 2,
            "riff_id": "00dfd5fa-686e-4699-8fc6-53b61a983246",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 3,
            "riff_id": "b2329b1c-409b-4610-ba35-9f7a9070dd1e",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 4,
            "riff_id": "735f55b3-84a9-4a77-8f6f-76a14e0135be",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 5,
            "riff_id": "39eb4025-9a26-4b4e-8146-051004acc25f",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 6,
            "riff_id": "e7d5ac82-a66b-47a4-a5c2-7ff886d37cee",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 7,
            "riff_id": "f3f09615-6938-45e3-9a46-eb381f4a7681",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 8,
            "riff_id": "81d9ca8e-0b3d-48b8-b845-0217b93bb0d0",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 9,
            "riff_id": "e0cbc581-d05e-4a6c-a6dd-487dc6dff91f",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 10,
            "riff_id": "c33fc346-c75e-4572-b684-66804e874bca",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 11,
            "riff_id": "47fb75dc-9017-46b0-ad3a-a4338145b8b3",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 12,
            "riff_id": "8e28adcd-b849-453c-8e6c-c4ae58d691d0",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 13,
            "riff_id": "7a51eb6f-97a3-48d5-804b-72b7c6db6273",
        },
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 14,
            "riff_id": "89f4c1cd-099d-40be-a4b8-cfeb0483ff68",
        },
    ]
}
response = requests.post(f"{IMPROVISER_HOST}/v1/exercises/", json=payload, headers=quick_auth_headers)
if response.status_code not in [200, 201, 204]:
    print(f"Error while creating exercise. Status: {response.status_code} with content: {response.content}")
else:
    print(f"Added exercise, with response {response.json()}")
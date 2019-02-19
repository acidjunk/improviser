"""
Create an exercise via the REST endpoint
"""
import sys

import datetime
import json
import os

import requests
import uuid

from client_examples.config import IMPROVISER_HOST

API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")

if not API_USER or not API_PASS:
    sys.exit("Please set needed environment vars.")


def login():
    default_headers = {"content-type": "application/json"}
    response = requests.post(IMPROVISER_HOST + "/login",
                             data=json.dumps({"email": API_USER, "password": API_PASS}),
                             headers=default_headers).json()
    token = response["response"]["user"]["authentication_token"]  # set token value
    user_id = response["response"]["user"]["id"]
    auth_headers = {**default_headers, "Authentication-Token": token}
    print("Auth header initialised")
    response = requests.get(IMPROVISER_HOST + '/v1/users/current-user', headers=auth_headers).json()
    quick_auth_headers = {**default_headers, "Quick-Authentication-Token": f"{user_id}:{response['quick_token']}"}
    print(f"Quick auth header initialised: Quick-Token: {quick_auth_headers}")
    return auth_headers, quick_auth_headers


# Starting MAIN
if os.getenv("QUICK_TOKEN"):
    print("Using OS provided QUICK_TOKEN")
    default_headers = {"content-type": "application/json"}
    quick_auth_headers = {**default_headers, "Quick-Authentication-Token": os.getenv("QUICK_TOKEN")}
else:
    _, quick_auth_headers = login()

NAME = "Chromatics adventure"

response = requests.get(f"{IMPROVISER_HOST}/v1/exercises", headers=quick_auth_headers).json()
names = [exercise["name"] for exercise in response]
found = False
counter = 1
while not found:
    if f"{NAME} {counter}" not in names:
        NAME = f"{NAME} {counter}"
        found = True
    counter += 1

exercise_id = str(uuid.uuid4())

payload = {
    "id": exercise_id,
    "name": NAME,
    "description": "Chromatics stuff",
    "root_key": "c",
    "is_public": False,
    "annotations":  [
        {"from": 0, "to": 1, "label": "Bm pent", "text": "B mineur pent, 3 maten, B blues minor"},
        {"from": 10, "to": 11, "label": "Bm pent", "text": "kan ook C groot of D dorisch twee maten lang"}
    ],
    "exercise_items": [
        {
            "pitch": "c",
            "octave": 0,
            "order_number": 0,
            "riff_id": "5ed49fc9-cd1c-4151-9ef5-20351fd57e45",
            "chord_info": "*Cm7",
            "number_of_bars": 2
        },
        {
            "pitch": "cis",
            "octave": 0,
            "order_number": 0,
            "riff_id": "5ed49fc9-cd1c-4151-9ef5-20351fd57e45",
            "chord_info": "*C#m7",
            "number_of_bars": 2
        },

    ],
    "tempo": 80
}

response = requests.post(f"{IMPROVISER_HOST}/v1/exercises/", json=payload, headers=quick_auth_headers)
if response.status_code not in [200, 201, 204]:
    print(f"Error while creating exercise. Status: {response.status_code} with content: {response.content}")
else:
    print(f"Added exercise, with response {response.json()}")

answer = input("Copy exercise? y/n: ")
if answer[0].lower() == "n":
    sys.exit()

payload = {"new_exercise_id": str(uuid.uuid4())}
response = requests.post(f"{IMPROVISER_HOST}/v1/exercises/copy/{exercise_id}", json=payload, headers=quick_auth_headers)
if response.status_code not in [200, 201, 204]:
    print(f"Error while copying exercise. Status: {response.status_code} with content: {response.content}")
else:
    print(f"Copied exercise, with response {response.json()}")

payload = {"new_exercise_id": str(uuid.uuid4())}
response = requests.post(f"{IMPROVISER_HOST}/v1/exercises/copy/{exercise_id}", json=payload, headers=quick_auth_headers)
if response.status_code not in [200, 201, 204]:
    print(f"Error while copying exercise. Status: {response.status_code} with content: {response.content}")
else:
    print(f"Copied exercise, with response {response.json()}")
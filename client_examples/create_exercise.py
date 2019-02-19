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

exercise_id = str(uuid.uuid4())

payload = {
    "id": exercise_id,
    "name": "Every summer night - date: " + str(datetime.datetime.now()),
    "description": "Chords on all bars of Every summer night",
    "root_key": "c",
    "is_public": False,
    "exercise_items": [
        {
            "pitch": "b",
            "octave": 0,
            "order_number": 0,
            "riff_id": "afa5f88a-147b-4471-ac71-4a8d89948ab1",
            "chord_info": "*Bm9",
        },
        {
            "pitch": "a",
            "octave": 0,
            "order_number": 1,
            "riff_id": "080286dd-0ac2-4bb9-9269-e70a4c049167",
            "chord_info": "*Am9",
        },
        {
            "pitch": "g",
            "octave": 0,
            "order_number": 2,
            "riff_id": "afa5f88a-147b-4471-ac71-4a8d89948ab1",
            "chord_info": "*Gm9 Am9",
        },
        {
            "pitch": "a",
            "octave": 0,
            "order_number": 3,
            "riff_id": "3f1cc1a4-905d-4311-befd-eb2d33ae1216",
            "chord_info": "*BbM7 Gm",
        },
        {
            "pitch": "d",
            "octave": 0,
            "order_number": 4,
            "riff_id": "afa5f88a-147b-4471-ac71-4a8d89948ab1",
            "chord_info": "*Dm9"
        },
        {
            "pitch": "g",
            "octave": 0,
            "order_number": 5,
            "riff_id": "c1c7c6f4-74b3-45a1-a1c5-d17e25e8200a",
            "chord_info": "*G9 Gm9",
        },

        {
            "pitch": "e",
            "octave": 0,
            "order_number": 6,
            "riff_id": "cc072e60-ff4c-41b1-b1b3-634de5b32cf8",
            "chord_info": "*F Eb"
        },
        {
            "pitch": "a",
            "octave": 0,
            "order_number": 7,
            "riff_id": "c69affc8-d504-4c97-bf46-6c566054bfb8",
            "chord_info": "*Bb Gm"
        },
        {
            "pitch": "f",
            "octave": 0,
            "order_number": 8,
            "riff_id": "89f4c1cd-099d-40be-a4b8-cfeb0483ff68",
            "chord_info": "*F G"
        },
        {
            "pitch": "e",
            "octave": 0,
            "order_number": 9,
            "riff_id": "53e6e122-6af6-403b-a8ce-6e1d757724fd",
            "chord_info": "*Em7 Em6"
        },
        {
            "pitch": "d",
            "octave": 0,
            "order_number": 10,
            "riff_id": "c33fc346-c75e-4572-b684-66804e874bca",
            "chord_info": "*Dm7 *Dm7"
        },
        {
            "pitch": "b",
            "octave": 0,
            "order_number": 11,
            "riff_id": "afa5f88a-147b-4471-ac71-4a8d89948ab1",
            "chord_info": "*Bm9",
        },
        {
            "pitch": "a",
            "octave": 0,
            "order_number": 12,
            "riff_id": "080286dd-0ac2-4bb9-9269-e70a4c049167",
            "chord_info": "*Am9",
        },
        {
            "pitch": "g",
            "octave": 0,
            "order_number": 13,
            "riff_id": "afa5f88a-147b-4471-ac71-4a8d89948ab1",
            "chord_info": "*Gm9 Am9",
        },
        {
            "pitch": "a",
            "octave": 0,
            "order_number": 14,
            "riff_id": "0b66bc70-58d1-4305-b6cd-ace7adf66eec",
            "chord_info": "*BbM7 Gm",
        },
        {
            "pitch": "d",
            "octave": 0,
            "order_number": 15,
            "riff_id": "afa5f88a-147b-4471-ac71-4a8d89948ab1",
            "chord_info": "*Dm9"
        },
        {
            "pitch": "g",
            "octave": 0,
            "order_number": 16,
            "riff_id": "c1c7c6f4-74b3-45a1-a1c5-d17e25e8200a",
            "chord_info": "*G9 Gm9",
        },

        {
            "pitch": "e",
            "octave": 0,
            "order_number": 17,
            "riff_id": "4ffb771d-d443-4237-bc93-719c329d35a1",
            "chord_info": "*F Eb"
        },
        {
            "pitch": "bes",
            "octave": 0,
            "order_number": 18,
            "riff_id": "17aaf175-a7ed-4419-b76e-3620a38725e4",
            "chord_info": "*Bb Gm"
        },
        {
            "pitch": "f",
            "octave": 0,
            "order_number": 19,
            "riff_id": "bdd2b9a2-2127-4136-8fa1-75336e1d5ab0",
            "chord_info": "*F G"
        },
        {
            "pitch": "e",
            "octave": 0,
            "order_number": 20,
            "riff_id": "53e6e122-6af6-403b-a8ce-6e1d757724fd",
            "chord_info": "*Em7 Em6"
        },
        {
            "pitch": "d",
            "octave": 0,
            "order_number": 21,
            "riff_id": "c33fc346-c75e-4572-b684-66804e874bca",
            "chord_info": "*Dm7 *Dm7"
        },
    ]
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
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

# payload = {
#     "id": exercise_id,
#     "name": "Test" + exercise_id,
#     "description": "Good stuff testing 2-5-1 chords",
#     "root_key": "c",
#     "is_public": False,
#     "exercise_items": [
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 0,
#             "riff_id": "61c290ec-9734-4364-b2ad-abf0b8ead3c2",
#             "chord_info": "blaat",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 1,
#             "riff_id": "3ef38750-f5d4-49c9-a422-aa01dfb8bb58",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 2,
#             "riff_id": "00dfd5fa-686e-4699-8fc6-53b61a983246",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "b2329b1c-409b-4610-ba35-9f7a9070dd1e",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 4,
#             "riff_id": "735f55b3-84a9-4a77-8f6f-76a14e0135be",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 5,
#             "riff_id": "39eb4025-9a26-4b4e-8146-051004acc25f",
#         },
#         {
#             "pitch": "f",
#             "octave": 0,
#             "order_number": 6,
#             "riff_id": "e7d5ac82-a66b-47a4-a5c2-7ff886d37cee",
#         },
#         {
#             "pitch": "ees",
#             "octave": 0,
#             "order_number": 7,
#             "riff_id": "f3f09615-6938-45e3-9a46-eb381f4a7681",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 8,
#             "riff_id": "81d9ca8e-0b3d-48b8-b845-0217b93bb0d0",
#         },
#         {
#             "pitch": "b",
#             "octave": 0,
#             "order_number": 9,
#             "riff_id": "e0cbc581-d05e-4a6c-a6dd-487dc6dff91f",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 10,
#             "riff_id": "c33fc346-c75e-4572-b684-66804e874bca",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 11,
#             "riff_id": "47fb75dc-9017-46b0-ad3a-a4338145b8b3",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 12,
#             "riff_id": "8e28adcd-b849-453c-8e6c-c4ae58d691d0",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 13,
#             "riff_id": "7a51eb6f-97a3-48d5-804b-72b7c6db6273",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 14,
#             "riff_id": "89f4c1cd-099d-40be-a4b8-cfeb0483ff68",
#         },
#     ]
# }
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
# payload = {
#     "id": exercise_id,
#     "name": "Band: " + str(datetime.datetime.now()),
#     "description": "Chords on all bars of Every summer night",
#     "root_key": "c",
#     "is_public": False,
#     "exercise_items": [
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 0,
#             "riff_id": "19c53d54-5c1d-4a58-8e26-12cb34a52d5f",
#             "chord_info": "*KWARTEN 1",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 0,
#             "riff_id": "9ef14d4f-7a6a-4782-9fc4-fd579b7c1ec6",
#             "chord_info": "*KWARTEN 1",
#         },
#         {
#             "pitch": "c",
#             "octave": 0,
#             "order_number": 0,
#             "riff_id": "2ba196a2-4a5d-42b9-9b84-61efc8a3a7c6",
#             "chord_info": "*KWARTEN 1",
#         },
#         {
#             "pitch": "fis",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "6b98e154-7749-4d68-9d14-3e9eac2c2a1d",
#             "chord_info": "*F# Maj",
#         },
#         {
#             "pitch": "fis",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "c0595373-32de-428c-a1bf-3ed92615bd82",
#             "chord_info": "*F# Maj",
#         },
#         {
#             "pitch": "fis",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "3bb742e9-0e79-4882-93ab-03b1886f90ff",
#             "chord_info": "*F# Maj",
#         },
#         {
#             "pitch": "b",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "6b98e154-7749-4d68-9d14-3e9eac2c2a1d",
#             "chord_info": "*B Maj",
#         },
#         {
#             "pitch": "b",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "c0595373-32de-428c-a1bf-3ed92615bd82",
#             "chord_info": "*B Maj",
#         },
#         {
#             "pitch": "b",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "3bb742e9-0e79-4882-93ab-03b1886f90ff",
#             "chord_info": "*B Maj",
#         },
#         {
#             "pitch": "a",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "6b98e154-7749-4d68-9d14-3e9eac2c2a1d",
#             "chord_info": "*A Maj",
#         },
#         {
#             "pitch": "a",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "c0595373-32de-428c-a1bf-3ed92615bd82",
#             "chord_info": "*A Maj",
#         },
#         {
#             "pitch": "a",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "3bb742e9-0e79-4882-93ab-03b1886f90ff",
#             "chord_info": "*A Maj",
#         },
#         {
#             "pitch": "e",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "6b98e154-7749-4d68-9d14-3e9eac2c2a1d",
#             "chord_info": "*E Maj",
#         },
#         {
#             "pitch": "e",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "c0595373-32de-428c-a1bf-3ed92615bd82",
#             "chord_info": "*E Maj",
#         },
#         {
#             "pitch": "e",
#             "octave": 0,
#             "order_number": 3,
#             "riff_id": "3bb742e9-0e79-4882-93ab-03b1886f90ff",
#             "chord_info": "*E Maj",
#         },
#
#     ]
# }
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
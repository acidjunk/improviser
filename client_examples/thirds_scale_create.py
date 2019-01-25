# Generate broken chord for M7, m7 en Dominant 7 chords in such a way that you get riffs that start on each chord note to ensure maximum instrument efficency
import sys

import json
import os
from collections import deque

import requests

from client_examples.config import IMPROVISER_HOST

note_numbers = range(1, 8)

template_notes = {
    "Thirds up over Major scale with eights:Cmaj":
        ["c'", "e'", "d'", "f'", "e'", "g'", "f'", "a'", "g'", "b'", "a'", "c''", "b'", "d''",
         "c''", "e''", "d''", "f''", "e''", "g''", "f''", "a''", "g''", "b''", "a''", "c'''", "b''", "d'''"],
    "Thirds down over Major scale with eights:Cmaj":
        ["c'''", "a''", "b''", "g''", "a''", "f''", "g''", "e''", "f''", "d''", "e''", "c''", "d''",
         "b'", "c''", "a'", "b'", "g'", "a'", "f'", "g'", "e'", "f'", "d'", "e'", "c'", "d'", "b", "c'", "b"],
    # Todo: add all turnarounds and all alternative endings
}

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
for description, notes in template_notes.items():
    for note_number in note_numbers:
        # use each note as a starting point once
        riff = []
        title, chord = description.split(":")
        name = title
        if note_number != 1:
            name = f"{name} starting on {note_number}"
        print(name)
        note_collection = deque(notes)
        note_collection.rotate((-note_number*2)+2)
        for i in range(16):
            riff.append(f"{note_collection[i]} ")
        riff[0] = f"{riff[0].strip()}8 "
        riff_string = "".join(riff).strip()
        print(riff_string)

        payload = {
            "name": name,
            "number_of_bars": 2,
            "notes": riff_string,
            "chord": chord,
            "multi_chord": False,
            "scale_trainer_enabled": True if note_number == 1 else False,
            "chord_info": "c1:maj c1:maj"
        }
        response = requests.post(f"{IMPROVISER_HOST}/v1/riffs/", json=payload, headers=auth_headers)
        if response.status_code not in [200, 201, 204]:
            print(f"Error while updating riff. Status: {response.status_code} with content: {response.content}")
        else:
            print(f"Added riff, with response {response.json()}")

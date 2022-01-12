"""
This script collects all chord files and uses the api to create the new backing tracks

It will output the mp3's with correct naming in `output/s3`. You can easily uipload it from there in
bulk to the corresponding Amazon S3 bucket.
"""
import os
import sys
from shutil import copyfile

import requests
import structlog

# Default to local running instance for now
IMPROVISER_HOST = "https://api.improviser.education"
# IMPROVISER_HOST = "http://localhost:5000"
ENDPOINT_BACKING_TRACKS = IMPROVISER_HOST + "/v1/backing-tracks"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
S3_PATH = os.path.join(OUTPUT_PATH, 's3')

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')

logger = structlog.get_logger(__name__)

if not API_USER or not API_PASS:
    sys.exit('Error: Please set needed environment vars.')

if not os.path.exists(S3_PATH) or not os.path.exists(OUTPUT_PATH):
    sys.exit('Error: Please ensure that both the output folder and s3 bucket folder exist.')

session = requests.Session()
data = {"email": API_USER, "password": API_PASS}
url = f"{IMPROVISER_HOST}/login"
response = session.post(url, data=data)

uploaded_files = []
for file in os.listdir(OUTPUT_PATH):
    if file.endswith(".txt"):
        backing_track_name = " - ".join(file.split(" - ")[0:2])
        audio_file_name = file.replace(".txt", "") + " Render.mp3"
        with open(os.path.join(OUTPUT_PATH, file), "r") as chord_reader:
            print(f"Handling {file}")
            chord_info = chord_reader.read()
            payload = {"name": backing_track_name, "tempo": 80, "chord_info": chord_info, "count_in": 6,
                       "intro_number_of_bars": 0, "number_of_bars": 121, "coda_number_of_bars": 1}
            response = session.post(ENDPOINT_BACKING_TRACKS, json=payload)
            if response.status_code != 201:
                print(f"error uploading {file}, payload: {payload}")
                print(f"List of already handled ID's: {uploaded_files}")
                sys.exit()
            backing_track_id = response.json()["id"]
            print(f"Added backing track with id: {backing_track_id}")
            payload["file"] = f"{backing_track_id}.mp3"
            response = session.put(ENDPOINT_BACKING_TRACKS + f"/{backing_track_id}", json=payload)
            if response.status_code != 201:
                print(f"error updating backing track with id: {backing_track_id}, payload: {payload}")
                print(f"List of already handled ID's: {uploaded_files}")
                sys.exit()
            uploaded_files.append(backing_track_id)
        copyfile(os.path.join(OUTPUT_PATH, audio_file_name), os.path.join(S3_PATH, f"{backing_track_id}.mp3"))

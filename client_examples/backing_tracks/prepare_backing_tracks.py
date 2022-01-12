"""
This script collects all SGU files and copy them to the output folder respecting the naming scheme.
"""
import glob
import json
import os
import sys
from shutil import copyfile

import requests
import structlog
import xmltodict
from boto3.s3.transfer import S3Transfer
import boto3

# Default to local running instance for now (faster and cheaper chord lookup)
# IMPROVISER_HOST = "https://api.improviser.education"
IMPROVISER_HOST = "http://localhost:5000"
ENDPOINT_RIFFS = IMPROVISER_HOST + "/v1/riffs"
ENDPOINT_EXERCISES = IMPROVISER_HOST + "/v1/exercises"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = "improviser.education"

logger = structlog.get_logger(__name__)
session = requests.Session()


# if not API_USER or not API_PASS or not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
#     sys.exit('Please set needed environment vars.')


def get_list_of_files(folder):
    # create a list of file and sub directories
    # names in the given directory
    lislist_of_files = os.listdir(folder)
    all_files = list()
    # Iterate over all the entries
    for entry in lislist_of_files:
        # Create full path
        fullPath = os.path.join(folder, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath) and "output" not in fullPath:
            all_files = all_files + get_list_of_files(fullPath)
        elif fullPath.endswith(".SGU"):
            all_files.append(fullPath)
        else:
            pass

    return all_files


def get_file_name_from_path(complete_path):
    parts = complete_path.split("/")
    file_name = parts[-1]
    bpm = parts[-2]
    assert "bpm" in bpm
    rest = " - ".join(parts[1:-2])
    return f"{rest} - {bpm} - {file_name}"


def copy_chord_files(complete_path, file_name):
    parts = complete_path.split("/")
    chord_file = os.path.join(parts[0], parts[1], parts[2], "chords.txt")
    pitch = file_name.split(" - ")[-1].replace('.SGU', '').lower()
    file_name = file_name.replace(".SGU", ".txt")
    with open(chord_file, "r") as chord_reader:
        chords = chord_reader.read()
        chord_list = chords.split(" ")
        print(chord_list)
        # print(pitch)
        transposed_chord_list = []
        for chord in chord_list:
            data = {"chord_info": chord, "pitch": pitch}
            response = session.post(ENDPOINT_EXERCISES + "/transpose-riff", json=data)
            if response.status_code != 200:
                print(f"error resolving: {chord} for {file_name}")
                sys.exit()
            transposed_chord_list.append(response.json()["chord_info"])
        with open(os.path.join(OUTPUT_PATH, file_name), "w") as chord_writer:
            print(transposed_chord_list)
            chord_writer.write(" ".join(transposed_chord_list))


if __name__ == "__main__":
    files = get_list_of_files(".")
    # print(files)
    for file in files:
        file_name = get_file_name_from_path(file)
        print(file_name)
        # copyfile(file, os.path.join(OUTPUT_PATH, file_name))
        copy_chord_files(file, file_name)

"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.

It has a check that ensures that only one instance can be running at the same time
"""
import glob
import json
import os
import sys

import requests
from boto3.s3.transfer import S3Transfer
import boto3

from render.render import Render, SIZES

DISABLE_CLEAN = os.getenv('DISABLE_CLEAN', 0)
LOCAL_RUN = os.getenv('LOCAL_RUN', False)
ENDPOINT_RIFFS = "https://api.improviser.education/riffs"
RENDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rendered')

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID') 
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY') 
AWS_BUCKET_NAME = "improviser.education"


renderer = Render(renderPath=RENDER_PATH)

pid = str(os.getpid())
pidfile = "/tmp/render_new_riffs.pid"

if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    sys.exit()
open(pidfile, 'w').write(pid)

if not LOCAL_RUN:
    if not API_USER or not API_PASS or not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        sys.exit('Please set needed environment vars.')


def render(riff):
    keys = ['c', 'cis', 'd', 'dis', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'aes', 'a', 'ais', 'bes', 'b']


    for key in keys:
        renderer.name = "riff_%s_%s" % (riff["id"], key)
        notes = riff["notes"].split(" ")
        renderer.addNotes(notes)
        renderer.set_cleff('treble')
        renderer.doTranspose(key)
        if not renderer.render():
            print("Error: couldn't render riff.id: {}".format(riff['id']))


def sync():
    """Sync all .png files to S3 bucket."""
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    transfer = S3Transfer(client)
    for size in SIZES:
        os.chdir(os.path.join(RENDER_PATH, str(size)))
        for file in glob.glob('*.png'):
            print("uploading file => {}".format(file)) 
            result = transfer.upload_file(file, AWS_BUCKET_NAME, "static/rendered/{}/{}".format(str(size), file))


def update_riffs(riff_ids):
    payload = {'render_valid': True}
    for riff_id in riff_ids:
        print("{}/rendered/{}".format(ENDPOINT_RIFFS, riff_id))
        print("Setting riff_id: {} to rendered -> True".format(riff_id))
        response = requests.put("{}/rendered/{}".format(ENDPOINT_RIFFS, riff_id), json=payload) 
        if response.status_code != 204:
            print("Error while updating riff")


def clean_garbage():
    extensions = ['eps', 'count', 'tex', 'texi']
    os.chdir(RENDER_PATH)
    print("Cleaning root *.ly")
    os.system('rm -f *.ly')
    for size in SIZES:
        for extension in extensions:
            print("Cleaning rm -f {folder}/*.{ext}".format(folder=size, ext=extension))
            os.system('rm -f {folder}/*.{ext}'.format(folder=size, ext=extension))


def cleanpng():
    extensions = ['png']
    os.chdir(RENDER_PATH)
    for size in SIZES:
        for extension in extensions:
            print("Cleaning rm -f {folder}/*.{ext}".format(folder=size, ext=extension))
            os.system('rm -f {folder}/*.{ext}'.format(folder=size, ext=extension))


if __name__ == '__main__':
    sync()
    1/0
    response = requests.get("{}?show_unrendered=true".format(ENDPOINT_RIFFS))
    if response.status_code != 200:
        print("Unable to query riffs")
        sys.exit()
        os.unlink(pidfile)
    riffs = response.json()
    rendered_riffs = []
    for riff in riffs:
        if not riff["render_valid"]:
            print("Rendering {}".format(riff["name"]))
            render(riff)
            rendered_riffs.append(riff["id"])
            if not LOCAL_RUN:
                clean_garbage()

    if len(rendered_riffs):
        if not LOCAL_RUN:
            sync()
            update_riffs(rendered_riffs)
            if not DISABLE_CLEAN:
                print("Cleaning: as cleaning is enabled...")
                clean_png()
    os.unlink(pidfile)

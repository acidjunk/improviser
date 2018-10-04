"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.

It has a check that ensures that only one instance can be running at the same time. Note: for now python 3.4 compatible.
"""
import glob
import json
import os
import sys

import requests
from boto3.s3.transfer import S3Transfer
import boto3

from render.render import Render, SIZES

LOCAL_RUN = os.getenv('LOCAL_RUN', False)
ENDPOINT_RIFFS = "https://api.improviser.education/riffs"
RENDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rendered')

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID') 
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY') 
AWS_BUCKET_NAME = "improviser.education"
KEYS = ['c', 'cis', 'd', 'dis', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'aes', 'a', 'ais', 'bes', 'b']

renderer = Render(renderPath=RENDER_PATH)

if not LOCAL_RUN:
    if not API_USER or not API_PASS or not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        sys.exit('Please set needed environment vars.')


def render(riff):
    rendered_riff_ids =[]
    for key in KEYS:
        renderer.name = "riff_%s_%s" % (riff["id"], key)
        notes = riff["notes"].split(" ")
        renderer.addNotes(notes)
        renderer.set_cleff('treble')
        renderer.doTranspose(key)
        if not renderer.render():
            print("Error: couldn't render riff.id: {}".format(riff['id']))
        # try to find the svg and retrieve metadata
    riff_name = "riff_{}_c.svg".format(riff["id"])
    if os.path.exists("rendered/svg/{riff_name}".format(riff_name=riff_name)):
        rendered_riff_ids.append(riff['id'])
    else:
        print("Error: couldn't find rendered svg {}! Quitting...".format(riff_name))
        sys.exit()

    print("Rendered {} images: {}".format(len(rendered_riff_ids), rendered_riff_ids))


def sync():
    """Sync all .png and .svg files to S3 bucket."""
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    transfer = S3Transfer(client)
    for size in SIZES:
        os.chdir(os.path.join(RENDER_PATH, str(size)))
        for file in glob.glob('*.png'):
            print("uploading file => {}".format(file)) 
            result = transfer.upload_file(file, AWS_BUCKET_NAME, "static/rendered/{}/{}".format(str(size), file))
    os.chdir(os.path.join(RENDER_PATH, "svg"))
    for file in glob.glob('*.svg'):
        print("uploading file => {}".format(file)) 
        result = transfer.upload_file(file, AWS_BUCKET_NAME, "static/rendered/svg/{}".format(file),
                                      extra_args={"ContentType": "image/svg+xml"})


def update_riffs(riff_ids):
    payload = {'render_valid': True}
    for riff_id in riff_ids:
        print("{}/rendered/{}".format(ENDPOINT_RIFFS, riff_id))
        print("Setting riff_id: {} to rendered -> True".format(riff_id))
        response = requests.put("{}/rendered/{}".format(ENDPOINT_RIFFS, riff_id), json=payload) 
        if response.status_code not in [200, 201, 204]:
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


def clean_png():
    extensions = ['png']
    os.chdir(RENDER_PATH)
    for size in SIZES:
        for extension in extensions:
            print("Cleaning rm -f {folder}/*.{ext}".format(folder=size, ext=extension))
            os.system('rm -f {folder}/*.{ext}'.format(folder=size, ext=extension))


def retrieve_metadata(riff_ids):
    for riff_id in riff_ids:
        filelist = []
        for key in KEYS:
            for octave in ['-1', '1', '2']:
                filelist.append(("{}_{}".format(key, octave),
                                 "rendered/svg/riff_{}_{}_{}.svg".format(riff_id, key, octave)))
            filelist.append((key, "rendered/svg/riff_{}_{}.svg".format(riff_id, key)))

        for file_suffix, file_name in filelist:
            if(os.path.exists(file_name)):
                print("File {} => {}".format(file_suffix, file_name))
            else:
                # ERROR?????
                # Todo: comment remove after debugging
                # print("Error: file {} not found".format(file_name))
                pass


        # print(filelist)


if __name__ == '__main__':

    pid = str(os.getpid())
    pidfile = "/tmp/render_new_riffs.pid"

    if os.path.isfile(pidfile):
        print("%s already exists, exiting" % pidfile)
        sys.exit()
    open(pidfile, 'w').write(pid)

    response = requests.get("{}?show_unrendered=true".format(ENDPOINT_RIFFS))
    if response.status_code != 200:
        print("Unable to query riffs")
        os.unlink(pidfile)
        sys.exit()

    riffs = response.json()
    rendered_riffs = []
    for riff in riffs:
        if not riff["render_valid"]:
            print("Rendering {}".format(riff["name"]))
            render(riff)
            # todo check if we can find one of the .pngs' of the rendered file?
            rendered_riffs.append(riff["id"])
            if not LOCAL_RUN:
                clean_garbage()
                sync()
                update_riffs(rendered_riffs)
                clean_png()
    os.unlink(pidfile)
    clean_png()
    sync()

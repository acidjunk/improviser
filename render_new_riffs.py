"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.

It has a check that ensures that only one instance can be running at the same time
"""
import os
import sys

import requests

from render.render import Render

ENDPOINT_RIFFS = "https://api.improviser.education/riffs?show_unrendered=true"
RENDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rendered')

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')

renderer = Render(renderPath=RENDER_PATH)

pid = str(os.getpid())
pidfile = "/tmp/render_new_riffs.pid"

if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    sys.exit()
open(pidfile, 'w').write(pid)

if not API_USER or not API_PASS:
    sys.exit('Please set needed environment vars.')

def render(riff):
    keys = ['c', 'f', 'g']  # only c,f,g for now

    for key in keys:
        renderer.name = "riff_%s_%s" % (riff["id"], key)
        notes = riff["notes"].split(" ")
        renderer.addNotes(notes)
        renderer.set_cleff('treble')
        renderer.doTranspose(key)
        if not renderer.render():
            print("Error: couldn't render riff.id: {}".format(riff['id']))

def sync():
    pass

def clean():
    sizes = ['small', 'medium', 'large']
    extensions = ['eps', 'count', 'tex', 'texi', 'png']
    os.chdir(RENDER_PATH)
    os.system('rm -f *.ly')
    for size in sizes:
        for extension in extensions:
            os.system('rm -f {folder}/*.{ext}'.format(folder=size, ext=extension))



if __name__ == '__main__':
    response = requests.get(ENDPOINT_RIFFS)
    if response.status_code != 200:
        sys.exit("Unable to query riffs")
    riffs = response.json()
    for riff in riffs:
        render(riff)
    sync()
    #clean()
    os.unlink(pidfile)

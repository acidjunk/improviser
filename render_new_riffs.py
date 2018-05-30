"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.
"""
import os
import sys
import requests

from render.render import Render

ENDPOINT_RIFFS = "https://api.improviser.education/riffs?show_unrendered=true"

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')

renderer = Render(renderPath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rendered'))


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
            print(f"Error: couldn't render riff.id: {riff['id']}")


if __name__ == '__main__':
    response = requests.get(ENDPOINT_RIFFS)
    if response.status_code != 200:
        sys.exit("Unable to query riffs")
    riffs = response.json()
    for riff in riffs:
        if not riff.get("render_valid"):
            render(riff)

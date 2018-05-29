"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.
"""
import os
import sys
import requests

from render.render import Render

renderer = Render(renderPath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rendered'))


ENDPOINT_RIFFS = "https://api.improviser.education/riffs?show_unrendered=true"

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_PASS')

if not API_USER or not API_PASS:
    sys.exit('Please set needed environment vars.')

def render(riff):
    print(riff)


if __name__ == '__main__':
    response = requests.get(ENDPOINT_RIFFS)
    if response.status_code != 200:
        sys.exit("Unable to query riffs")
    riffs = response.json()
    for riff in riffs:
        if not riff.get("render_valid"):
            render(riff)

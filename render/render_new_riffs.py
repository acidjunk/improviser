"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.
"""
import os
import sys
import requests

ENDPOINT_RIFFS = "https://api.improviser.education/riffs"

API_USER = os.getenv('API_USER')
API_PASS = os.getenv('API_USER')

if not API_USER or not API_PASS:
    sys.exit('Please set needed environment vars.')

if __name__ == '__main__':
    riffs = requests.get(ENDPOINT_RIFFS)
    if riffs.status_code != 200:
        sys.exit("Unable to query riffs")
    print(riffs.content)

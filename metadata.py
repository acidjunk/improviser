"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.

It has a check that ensures that only one instance can be running at the same time.

Note: for now python 3.4 compatible.
"""
import requests

from render_new_riffs import retrieve_metadata, ENDPOINT_RIFFS

#response = requests.get("{}".format(ENDPOINT_RIFFS))
#riff_ids = [riff["id"] for riff in response.json()]
riff_ids = ["080286dd-0ac2-4bb9-9269-e70a4c049167"]
print(riff_ids)
print("Starting metadata extraction\n**************")
retrieve_metadata(riff_ids)

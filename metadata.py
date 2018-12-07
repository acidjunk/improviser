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
riff_ids = ["7d867eb5-3415-4e59-8762-267298f1d4a2", "8191402c-8ac1-4fb5-8e3c-61f8b5e94f52",
            "16e44ba5-4dc3-4d1c-9469-a30eec620ad7", "9880cfde-16cb-473b-9cbf-c1e020a5b900"]
print(riff_ids)
print("Starting metadata extraction\n**************")
retrieve_metadata(riff_ids, skip_update=True)

"""
This script will query https://api.improviser.education for unrendered riffs. It will then render them and
upload the rendered/changed riffs to an Amazon S3 bucket and flag the riff as rendered via a second API call.

It has a check that ensures that only one instance can be running at the same time.

Note: for now python 3.4 compatible.
"""
from render_new_riffs import retrieve_metadata

riff_ids = ['16e44ba5-4dc3-4d1c-9469-a30eec620ad7',
            '2392a94a-be9b-4360-b36a-9c53b195a25e',
            '5b0503b9-47e3-4684-a7a8-b0c1b4fc7ae9',
            'e14e181e-0b2a-4a4f-acba-eddd8692b5bf']

retrieve_metadata(riff_ids)
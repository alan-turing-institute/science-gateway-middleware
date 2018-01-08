#!/usr/bin/env python

from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings

# set credentials
block_blob_service = BlockBlobService(
    account_name='SECRET',
    account_key='SECRET')

# show existing blobs
generator = block_blob_service.list_blobs('blue')
for blob in generator:
    print(blob.name)

# upload a new blob
block_blob_service.create_blob_from_path(
    'blue',
    'test.png',
    'content.png',
    content_settings=ContentSettings(content_type='image/png')
            )





import os
job_id = 'UUID'
for f in outputs:
    basename = os.path.basename(f['source_uri'])
    destination_path = os.path.join(f['destination_path'], basename)
    block_blob_service.create_blob_from_path(
        'job_id',
        f['source_uri'],
        destination_path,
        content_settings=ContentSettings(content_type=f['content_type']))

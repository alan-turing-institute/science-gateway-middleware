#!/usr/bin/env python

from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings

# set credentials
block_blob_service = BlockBlobService(
    account_name='sgmiddleware',
    account_key='Lo7QSq3FspUifKH1vHVc0hqgfuJZktiZYxMIdeq38Hd6lWLwkO/4MOarljlLHD//27GDpZJuJ8eWv94Dkr5T/Q==')

# show existing blobs
generator = block_blob_service.list_blobs('test')
for blob in generator:
    print(blob.name)

# upload a new blob
block_blob_service.create_blob_from_path(
    'test',
    'transferred.png',
    'content.png',
    content_settings=ContentSettings(content_type='image/png'))


# import os
# job_id = 'UUID'
# for f in outputs:
#     basename = os.path.basename(f['source_uri'])
#     destination_path = os.path.join(f['destination_path'], basename)
#     block_blob_service.create_blob_from_path(
#         'test',
#         f['source_uri'],
#         destination_path,
#         content_settings=ContentSettings(content_type=f['content_type']))

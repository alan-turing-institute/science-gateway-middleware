#!/bin/bash

JOB_ID=$(cat bin/job_id)
JOB_STORAGE_TOKEN=$(cat bin/job_storage_token)
PBS_JOB_ID=$(cat bin/pbs_job_id)

ACCOUNT='sgmiddleware'
CONTAINER='openfoam'
BLOB_STEM_NAME=$JOB_ID

lockdir='.lock_storage_sync'

mkdir $lockdir  || {
    echo "lock directory exists. exiting"
    exit 1
}

# remove lock directory
trap "rmdir $lockdir" EXIT INT KILL TERM

# transfer files to cloud storage
/home/vm-admin/miniconda/bin/blobxfer upload \
    --sas "$JOB_STORAGE_TOKEN" \
    --storage-account $ACCOUNT \
    --remote-path $CONTAINER/$JOB_ID \
    --local-path . \
    --no-overwrite \
    --recursive

# fine-grained control over overwrite decision
#--skip-on-filesize-match
#--skip-on-lmt-ge  (most approriate?)
#--skip-on-md5-match

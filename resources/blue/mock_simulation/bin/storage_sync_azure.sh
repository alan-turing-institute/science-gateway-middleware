#!/bin/bash

JOB_ID=$(cat bin/job_id)
PBS_JOB_ID=$(cat bin/pbs_job_id)

CONTAINER='openfoam'
BLOB_STEM_NAME=$JOB_ID

lockdir='.lock_storage_sync'

mkdir $lockdir  || {
    echo "lock directory exists. exiting"
    exit 1
}

# remove lock directory
trap "rmdir $lockdir" EXIT INT KILL TERM

# move files to mock storage
# rclone sync --include-from include-file.txt output remote:$CONTAINER/$BLOB_STEM_NAME
rclone sync . Azure:$CONTAINER/$BLOB_STEM_NAME

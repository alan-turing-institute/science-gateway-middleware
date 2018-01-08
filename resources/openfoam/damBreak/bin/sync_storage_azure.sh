#!/bin/bash

CONTAINER='rclone'
BLOB_STEM_NAME='jobid'

lockdir='.lock_rclone'

mkdir $lockdir  || {
    echo "lock directory exists. exiting"
    exit 1
}

# remove lock directory
trap "rmdir $lockdir" EXIT INT KILL TERM

# move files to mock storage
# rclone sync --include-from include-file.txt output remote:$CONTAINER/$BLOB_STEM_NAME
rclone sync . Azure:$CONTAINER/$BLOB_STEM_NAME

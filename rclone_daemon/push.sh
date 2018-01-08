#!/bin/bash

CONTAINER='rclone'
JOB_ID='jobid'

lockdir='.lock_rclone'

mkdir $lockdir  || {
    echo "lock directory exists. exiting"
    exit 1
}
# take pains to remove lock directory when script terminates
trap "rmdir $lockdir" EXIT INT KILL TERM

# move files to mock storage
rclone sync --include-from include-file.txt output remote:$CONTAINER/$JOB_ID

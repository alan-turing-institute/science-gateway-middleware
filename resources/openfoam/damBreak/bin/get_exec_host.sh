#!/bin/bash

PBS_JOB_ID=$(cat bin/pbs_job_id)

# Example: parses "    exec_host = cx1-50-3-2/13 " into "cx1-50-3-2"
qstat -f $PBS_JOB_ID | grep 'exec_host' | awk -F= '{print $2}' | awk -F/ '{print $1}' | tr -d ' '

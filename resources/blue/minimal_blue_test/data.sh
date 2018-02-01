#!/bin/bash

# create a file named `pbs_job_identifier`
# which contains the pbs id (example: "5309476.cx1b")
# use `tee` to retain stdout

PBS_JOB_ID=$(cat pbs_job_id)
EXEC_HOST=$(bash get_exec_host.sh)
TMPDIR="/tmp/pbs.$PBS_JOB_ID"

ssh $EXEC_HOST "cd $TMPDIR && python csv_to_data_json.py"

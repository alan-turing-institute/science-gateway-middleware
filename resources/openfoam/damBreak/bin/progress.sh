#!/bin/bash

PBS_JOB_ID=$(cat bin/pbs_job_id)
EXEC_HOST=$(bash bin/get_exec_host.sh)
TMPDIR="/tmp/pbs.$PBS_JOB_ID"

ssh $EXEC_HOST "cd $TMPDIR && python bin/csv_to_progress_json.py"

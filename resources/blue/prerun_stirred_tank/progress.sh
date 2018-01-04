#!/bin/bash

PBS_JOB_ID=$(cat pbs_job_id)
EXEC_HOST=$(bash get_exec_host.sh)
TMPDIR="/tmp/pbs.$PBS_JOB_ID"

if [ -n "$EXEC_HOST" ]
then
  ssh $EXEC_HOST "cd $TMPDIR && python csv_to_progress_json.py"
else
  python csv_to_progress_json.py
fi

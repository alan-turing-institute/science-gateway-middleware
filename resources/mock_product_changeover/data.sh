#!/bin/bash

PBS_JOB_ID=$(cat pbs_job_id)
PBS_JOB_STATE=$(qstat $PBS_JOB_ID -x | grep -P -o "<job_state>\K.")
EXEC_HOST=$(bash get_exec_host.sh)
TMPDIR="/tmp/pbs.$PBS_JOB_ID"

if [ "$PBS_JOB_STATE" == "R" ]; then
  ssh $EXEC_HOST "cd $TMPDIR && python csv_to_data_json.py"
elif [ "$PBS_JOB_STATE" == "Q" ]; then
  exit 0
else
  python csv_to_data_json.py
fi

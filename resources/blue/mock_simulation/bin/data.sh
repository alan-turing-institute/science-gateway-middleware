#!/bin/bash

PBS_JOB_ID=$(cat pbs_job_id)
EXEC_HOST=$(bash get_exec_host.sh)
TMPDIR="/tmp/pbs.$PBS_JOB_ID"

ssh $EXEC_HOST "cd $TMPDIR && python csv_to_data_json.py"

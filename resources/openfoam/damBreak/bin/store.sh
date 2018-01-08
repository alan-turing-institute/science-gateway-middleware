#!/bin/bash

PBS_JOB_ID=$(cat bin/pbs_job_id)
EXEC_HOST=$(bash bin/get_exec_host.sh)
TMPDIR="/tmp/pbs.$PBS_JOB_ID"

ssh $EXEC_HOST "cd $TMPDIR && bash bin/sync_storage_azure.sh"

# TODO handle completed jobs (where storage will be from /work instead of compute node $TMPDIR)

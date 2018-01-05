#!/bin/bash

# create a file named `pbs_job_id`
# which contains the pbs id (example: "5309476.cx1b")
# use `tee` to retain stdout
qsub -k oe pbs.sh | tee bin/pbs_job_id
# qsub pbs.sh | tee pbs_job_id

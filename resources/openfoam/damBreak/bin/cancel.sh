#!/bin/sh

PBS_JOB_ID=$(cat bin/pbs_job_id)
qdel $PBS_JOB_ID

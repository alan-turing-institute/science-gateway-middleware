#!/bin/bash
#PBS -j oe
#PBS -o "TEST.out"

STORAGE_SCRIPT='./bin/storage_sync_azure.sh'
STORAGE_SYNC_FREQUENCY=10

echo "Start PBS"

# kill all child processes on exit
# note: this is likely handled automatically by the schedular
trap "exit" INT TERM
trap "kill 0" EXIT

set -vx

# emulate running in TMPDIR as per Imperial College cx1
TMPDIR="/tmp/pbs.$PBS_JOBID"

echo $TMPDIR

mkdir -p $TMPDIR

cp -r $PBS_O_WORKDIR/* $TMPDIR  # TODO explicitly copy only required files
cd $TMPDIR

# run storage daemon loop and collect its PID number
(while `true`; do $STORAGE_SCRIPT; sleep $STORAGE_SYNC_FREQUENCY; done) &
STORAGE_DAEMON_PID=$!

source /opt/openfoam5/etc/bashrc
./Allrun

# here we ensure cloud storage is complete, before local cluster storage

# STORAGE SYSTEM A: cloud provider storage
# kill storage daemon loop and ensure that it completes
# one full cycle

kill STORAGE_DAEMON_PID
$STORAGE_SCRIPT

# STORAGE SYSTEM B: local cluster storage
# copy back timestep information
for timestep in $(foamListTimes); do
  cp -r $TMPDIR/$timestep $PBS_O_WORKDIR
done

echo "End PBS"

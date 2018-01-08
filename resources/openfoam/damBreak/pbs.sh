#!/bin/bash
#PBS -j oe
#PBS -o "TEST.out"

STORAGE_SYNC_FREQUENCY=10

echo "Start PBS"

# kill all child processes on exit
# note: this is likely handled automatically by the schedular
# trap "exit" INT TERM
# trap "kill 0" EXIT

set -vx

# emulate running in TMPDIR as per Imperial College cx1
TMPDIR="/tmp/pbs.$PBS_JOBID"

echo $TMPDIR

mkdir -p $TMPDIR

cp -r $PBS_O_WORKDIR/* $TMPDIR  # TODO explicitly copy only required files
cd $TMPDIR

(while `true`; do ./bin/sync_storage_azure.sh; sleep $STORAGE_SYNC_FREQUENCY; done) &

source /opt/openfoam5/etc/bashrc
./Allrun

# copy back timestep information
for timestep in $(foamListTimes); do
  cp -r $TMPDIR/$timestep $PBS_O_WORKDIR
done


# wait for sync storage to complete
# (i.e. wait until lock directory has been removed)
sleep 30


echo "End PBS"

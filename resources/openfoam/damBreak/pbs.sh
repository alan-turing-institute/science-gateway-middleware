#!/bin/bash
#PBS -j oe
#PBS -o "TEST.out"

echo "Start PBS"

set -vx

# emulate running in TMPDIR as per Imperial College cx1
TMPDIR="/tmp/pbs.$PBS_JOBID"

echo $TMPDIR

mkdir -p $TMPDIR

cp -r $PBS_O_WORKDIR/* $TMPDIR  # TODO explicitly copy only required files
cd $TMPDIR

source /opt/openfoam5/etc/bashrc
./Allrun

# copy back timestep information
for timestep in $(foamListTimes); do
  cp -r $TMPDIR/$timestep $PBS_O_WORKDIR
done

echo "End PBS"

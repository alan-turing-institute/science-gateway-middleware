#!/bin/bash
#PBS -j oe
#PBS -o "TEST.out"

echo "Start PBS"

set -vx

# emulate running in TMPDIR as per Imperial College cx1
TMPDIR="/tmp/pbs.$PBS_JOBID"

echo $TMPDIR

mkdir -p $TMPDIR
cp $PBS_O_WORKDIR/mock_blue.py $TMPDIR
cp $PBS_O_WORKDIR/Blue.nml $TMPDIR
cp $PBS_O_WORKDIR/source.csv $TMPDIR
cp $PBS_O_WORKDIR/csv_to_data_json.py $TMPDIR
cp $PBS_O_WORKDIR/csv_to_progress_json.py $TMPDIR

cd $TMPDIR

python mock_blue.py  # emulate `mpiexec ./$PROGRAM`

cp $TMPDIR/*.csv $PBS_O_WORKDIR

echo "End PBS"

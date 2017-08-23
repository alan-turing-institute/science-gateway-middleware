#!/bin/bash
#PBS -N TEST
#PBS -o TEST.out
#PBS -j oe
#PBS -lselect=1:ncpus=2:icib=true
#PBS -lwalltime=00:10:00
#PBS -m be
#PBS -M l.mason@imperial.ac.uk

set -vx
cd $TMPDIR

PROJECT="from_middleware"  # TODO name using submission directory name
PROGRAM="aeration.x"

# Transfer Blue.nml file
cp $PBS_O_WORKDIR/Blue.nml $TMPDIR
cp $PBS_O_WORKDIR/$PROGRAM $TMPDIR

# Create the project working directory
[ -d $WORK/$PROJECT ] || mkdir -p $WORK/$PROJECT

RESTART=$(grep 'restart=' Blue.nml | awk -F"=" '{print $2}' | awk '{print toupper($1)}')
RESTART_INDEX=$(grep 'input_file_index' Blue.nml | awk -F"=" '{print $3}' | awk '{print $1}')

# Load Restart or initial files
if [[ $RESTART == ".TRUE." ]]
then

  echo "... Loading restart files ${RESTART_INDEX} ..."
  pbsdsh2 cp -rf $WORK/$PROJECT/\*.csv $TMPDIR/.
  pbsdsh2 cp -rf $WORK/$PROJECT/\*.${RESTART_INDEX}.rst $TMPDIR/.
  pbsdsh2 cp -rf $WORK/$PROJECT/$PROGRAM $TMPDIR/$PROGRAM

else

  pbsdsh2 cp -pf $PBS_O_WORKDIR/$PROGRAM $TMPDIR/$PROGRAM
  if [[ ${RESTART_INDEX} != "0" ]]
  then

    echo "... Loading initialization files ${RESTART_INDEX} ..."
    pbsdsh2 cp -rf $WORK/$PROJECT/\*.${RESTART_INDEX}.rst $TMPDIR/.

  fi
fi

# Run the program.
echo "... Run started @ $(date) ..."
#module load intel-suite mpi
#module load intel-suite/2015.3 mpi/intel-5.1
module load intel-suite/2017.1 mpi/intel-5.1.1.109  # required for BLUE-11.2

#pbsexec -grace 55 mpiexec ./$PROGRAM ; OK=$?
mpiexec ./$PROGRAM ; OK=$?
echo "... Run finished @ $(date) with error code $OK ..."

if (( $OK == 0 ))
then

  # Save results in WORKDIR.
  echo "... Saving results in $WORK/$PROJECT ..."
  pbsdsh2 cp -rf $TMPDIR/\*.x   $WORK/$PROJECT/.
  pbsdsh2 cp -rf $TMPDIR/\*.rst $WORK/$PROJECT/.
  pbsdsh2 cp -rf $TMPDIR/\*.vt* $WORK/$PROJECT/.
  pbsdsh2 cp -rf $TMPDIR/\*.pvd $WORK/$PROJECT/.
  pbsdsh2 cp -rf $TMPDIR/\*.csv $WORK/$PROJECT/.
  pbsdsh2 cp -rf $TMPDIR/\*.dat $WORK/$PROJECT/.
  pbsdsh2 cp -rf $TMPDIR/\*.nml $WORK/$PROJECT/.
fi

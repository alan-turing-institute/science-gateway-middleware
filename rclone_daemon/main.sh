#!/bin/bash

PERIOD_PUSH=5  # wait this long (seconds) before syncing to Azure blob storage
PERIOD_WRITE=10  # wait this long (seconds) before writing next local mock simulation data

# kill all child processes on exit
trap "exit" INT TERM
trap "kill 0" EXIT

# set push running
(while `true`; do ./push.sh; sleep $PERIOD_PUSH; done) &

# main code (mock simulation)
mkdir -p output
for i in $(seq 100)
do
  date > output/$i.vtk
  sleep $PERIOD_WRITE
done

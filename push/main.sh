#!/bin/bash

# set push running


# main code
for i in $(seq 20)
do
  sleep 10
  date > $i.dat
done

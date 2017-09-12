#!/usr/bin/env python

import csv

from time import sleep
import random

dt = 1e-5


def time(timestep):
    return timestep * dt


def delay():
    sleep(7)


statement = """
 *** (C) MOCK MMXVI, release 11.2. All Rights Reserved.


 ... Reading input parameters ...

 ... Entering initial setup ...

 ... Entering timestep loop ...

 ... Setting initial pressure ...
 """

info = """
*** TIME INDEX:        {:5d}           |             REAL TIME:  {:10.4f}    ***
----------------------------------------------------------------------------------
max(|div(V)|):                                                          {:10.4f}
----------------------------------------------------------------------------------
"""


def stdout(timestep):
    time = timestep * dt
    print(info.format(timestep, time, random.random())+"\n")


csv_fname = 'output.csv'

source_fname = 'source.csv'
with open(source_fname, "r") as s:
    source_lines = s.readlines()

# write headers, "w" ensures file is flushed
with open(csv_fname, 'w') as csv_file:
    csv_file.write(source_lines[0])

# write data
for i in range(len(source_lines)):
    stdout(i)
    if i == 0:  # skip header
        continue
    else:
        with open(csv_fname, 'a') as csv_file:
            csv_file.write(source_lines[i])
            delay()

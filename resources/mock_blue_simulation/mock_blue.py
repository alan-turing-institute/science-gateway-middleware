#!/usr/bin/env python

import csv

from time import sleep
import random
import re

# example parameter settings
# (for testing with hardcoded parameters)

# timestep_max = 300
# dt = 1e-4
#
# initial_value = 10
# gradient = 400


# read parameters from mock input file
# for Blue, the input file is a fortran name list

def info(name, value):
    print('Loading parameter: {}={}'.format(name, value))

with open('Blue.nml', 'r') as f:
    parameter_lines = f.readlines()

for line in parameter_lines:

    initial_value_input = re.search(r'initial_value\s+=\s+(\S+)', line)
    gradient_input = re.search(r'gradient\s+=\s+(\S+)', line)
    timestep_max_input = re.search(r'timestep_max\s+=\s+(\S+)', line)
    dt_input = re.search(r'dt\s+=\s+(\S+)', line)

    if initial_value_input:
        initial_value = float(initial_value_input.group(1))
        info('initial_value', initial_value)
    if gradient_input:
        gradient = float(gradient_input.group(1))
        info('gradient', gradient)
    if timestep_max_input:
        timestep_max = int(timestep_max_input.group(1))
        info('timestep_max', timestep_max)
    if dt_input:
        dt = float(dt_input.group(1))
        info('dt', dt)


def time(timestep):
    return timestep * dt


def model_linear(timestep, initial_value=initial_value, gradient=gradient):
    return time(timestep) * gradient + initial_value


def model_noisy(time):
    return random.random()


def delay():
    sleep(1)


statement = """
 *** (C) BLUE MMXVI, release 11.2. All Rights Reserved.


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


# and write to this csv file
with open('output.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Time(s)', 'linear', 'noisy'])
    for timestep in range(timestep_max):
        stdout(timestep)
        linear = model_linear(timestep)
        noisy = model_noisy(timestep)
        writer.writerow([time(timestep), linear, noisy])
        delay()

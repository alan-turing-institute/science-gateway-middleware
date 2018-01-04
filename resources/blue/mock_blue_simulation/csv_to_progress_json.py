#!/usr/bin/env python

# return job progress, example output is

# {
#   "progress": {
#     "range_min": 0,
#     "range_max": 100,
#     "value": 0.0037375,
#     "units": "%"
#   }
# }

from __future__ import print_function  # for python 2 compatability

from collections import deque
import csv
import json
import re


def get_reference_value():

    with open('Blue.nml', 'r') as f:
        parameter_lines = f.readlines()

    for line in parameter_lines:
        timestep_max_input = re.search(r'timestep_max\s+=\s+(\S+)', line)
        if timestep_max_input:
            timestep_max = float(timestep_max_input.group(1))

    return timestep_max


def get_last_row(fname):
    with open(fname, 'r') as f:
        try:
            lastrow = deque(csv.reader(f), 1)[0]
        except IndexError:  # empty file
            lastrow = None
        return lastrow


def csv_to_progress_json(fname):
    with open(fname, 'r') as f:

        output = {
            "range_min": 0,
            "range_max": 100,
            "value": 0,
            "units": "%"
        }

        d_reader = csv.DictReader(f)
        headers = d_reader.fieldnames

        try:
            index = headers.index('timestep')
        except:
            # csv file is empty
            return {"progress": output}

        last_row = get_last_row(fname)
        latest_value = float(last_row[index])

        reference_value = get_reference_value()
        progress = latest_value/reference_value
        output["value"] = progress

        return {"progress": output}


progress_object = csv_to_progress_json("output.csv")

print(json.dumps(progress_object))  # print to stdout

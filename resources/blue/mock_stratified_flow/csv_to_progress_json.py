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

    reference_value = 0.0851890802  # hard-coded reference time for demo

    return reference_value


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
            "value": 100,
            "units": "%"
        }

        d_reader = csv.DictReader(f)
        headers = d_reader.fieldnames

        try:
            index = headers.index('Time')
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

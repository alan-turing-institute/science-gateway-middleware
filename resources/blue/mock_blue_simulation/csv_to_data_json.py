#!/usr/bin/env python

from __future__ import print_function  # for python 2 compatability

import csv
import json


def csv_to_data_json(fname, data_required=None):

    with open(fname, 'r') as f:
        d_reader = csv.DictReader(f)
        headers = d_reader.fieldnames

        columns_to_process = headers  # default to processing all csv columns
        column_labels = headers
        if data_required:
            columns_to_process = []
            column_labels = []
            for object_ in data_required:
                columns_to_process.append(object_['csv_variable'])
                column_labels.append(object_['label'])

        output = {
            "keys": columns_to_process,
            "labels": column_labels
        }

        # prepare data lists
        for name in columns_to_process:
            output[name] = []

        # populate data lists
        for line in d_reader:
            for name in columns_to_process:
                output[name].append(float(line[str(name)]))

        return {"data": output}


data_required = [
    {
        "csv_variable": "Time(s)",
        "label": "Time",
        "units": "s"
    },
    {
        "csv_variable": "linear",
        "label": "Linear quantity",
        "units": "kg"
    },
    {
        "csv_variable": "noisy",
        "label": "Random quantity",
        "units": "L"
    }
]

data_object = csv_to_data_json(
    "output.csv",
    data_required=data_required)

print(json.dumps(data_object))  # print to stdout


# The above code uses csv and json from the standard library
# pandas takes too long to load on cx1
# test this for yourself using the line below
# module load anaconda3; python -c "import pandas"

# The above code could be implemented concisely in pandas using
#
# import pandas as pd
# import json
# csv_variables_to_keep = ["Time(s)", "FLUID_VOLUME"]
# label_strings = ["Time (s)", "Fluid volume (-)"]
#
# df = pd.DataFrame(
#     pd.read_csv("aeration.csv", sep=",", header=0, index_col=False))
# df_output = df[csv_variables_to_keep]
#
# data_object = {"keys": csv_variables_to_keep, "labels": label_strings}
# for csv_variable in csv_variables_to_keep:
#     data_object[csv_variable] = df[csv_variable].values.tolist()
# print(json.dumps({"data": data_object}))

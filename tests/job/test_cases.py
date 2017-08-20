from middleware.job.schema import CaseSchema
from middleware.job.models import case_to_job

import json


# class TestCase(object):
#     def test_load_cases_from_json(self):
#
#         # load case objects from cases json file
#         with open('./resources/cases/blue_cases.json') as data_file:
#             data = json.load(data_file)
#
#         case_json = data[0]
#
#         case = CaseSchema().make_case(case_json)


# load case objects from cases json file
with open('./resources/cases/blue_cases.json') as data_file:
    data = json.load(data_file)

case_json = data[0]
case = CaseSchema().make_case(case_json)

job = case_to_job(case)

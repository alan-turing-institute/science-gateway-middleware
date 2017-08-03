import pytest
from middleware.job.model import is_valid_job_json, job_summary_json


class TestModel(object):
    def test_job_summary_json(self):

        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        test_json = {"id": job_id, "parameters": {"height": 3,
                     "width": 4, "depth": 5}}

        summary = job_summary_json(test_json)

        assert {"id": job_id} == summary

    def test_is_valid_job_json_invalid_job(self):
        test_json = {"parameters": {"height": 3, "width": 4, "depth": 5}}

        valid = is_valid_job_json(test_json)

        assert valid is False

    def test_is_valid_job_json_valid_job(self):
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        test_json = {"id": job_id, "parameters": {"height": 3,
                     "width": 4, "depth": 5}}

        valid = is_valid_job_json(test_json)

        assert valid is True

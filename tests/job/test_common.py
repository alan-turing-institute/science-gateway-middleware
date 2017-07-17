from middleware.job.common import JobApi, JobsApi
from middleware.job.inmemory import JobRepositoryMemory
from middleware.app import create_app
import unittest
import pytest
from werkzeug.exceptions import NotFound
import json


def json_to_response_data(json_data):
    # Add newline to JSON and encode as UTF-8
    return "{}\n".format(json.dumps(json_data)).encode("utf-8")


class TestJobApi(unittest.TestCase):

    def test_abort_if_not_found_throws_notfound_exception(self):
        jobs = JobRepositoryMemory()
        api = JobApi(job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        with pytest.raises(NotFound):
            api.abort_if_not_found(job_id)

    def test_get_for_existing_job_returns_job_with_200_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        jobs.create(job)
        self.app = create_app(jobs)
        self.client = self.app.test_client()
        job_response = self.client.get("/job/{}".format(job_id))
        assert job_response.status_code == 200
        assert job_response.data == json_to_response_data(job)

    def test_get_for_nonexistent_job_raises_not_found(self):
        jobs = JobRepositoryMemory()
        self.app = create_app(jobs)
        self.client = self.app.test_client()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = self.client.get("/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert job_response.data == json_to_response_data(error_message)


class TestJobsApi(object):

    def test_post_for_nonexistent_job_returns_job_with_200_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        self.app = create_app(jobs)
        self.client = self.app.test_client()
        job_response = self.client.post("/jobs", data=json.dumps(job),
                                        content_type='application/json')
        assert job_response.status_code == 200
        assert job_response.data == json_to_response_data(job)
        assert jobs.get_by_id(job_id) == job

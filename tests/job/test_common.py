from middleware.job.common import JobApi
from middleware.job.inmemory import JobRepositoryMemory
import pytest
from werkzeug.exceptions import NotFound


class TestJobApi(object):

    def test_abort_if_not_found_throws_notfound_exception(self):
        jobs = JobRepositoryMemory()
        api = JobApi(job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        with pytest.raises(NotFound):
            api.abort_if_not_found(job_id)

    def test_get_for_existing_job_retrieves_job_with_200(self):
        jobs = JobRepositoryMemory()
        api = JobApi(job_repository=jobs)
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        jobs.create(job)
        job_response = api.get(job_id)
        assert job_response == (job, 200)

    def test_get_for_nonexistent_job_raises_not_found(self):
        jobs = JobRepositoryMemory()
        api = JobApi(job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        with pytest.raises(NotFound):
            api.get(job_id)

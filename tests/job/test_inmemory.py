from middleware.job.inmemory import JobRepositoryMemory


class TestJobRepositoryMemory(object):

    def test_new_repo_has_no_jobs(self):
        repo = JobRepositoryMemory()
        # New repository onject should have empty jobs list
        assert len(repo._jobs) == 0

    def test_get_by_id(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo._jobs[job_id] = job
        job_ret = repo.get_by_id(job_id)
        assert(job_ret == job)

    def test_create_job(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo.create(job)
        job_ret = repo._jobs[job_id]
        assert(job_ret == job)

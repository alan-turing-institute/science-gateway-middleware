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
        job_returned = repo.get_by_id(job_id)
        assert(job_returned == job)

    def test_create_job(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        job_returned = repo.create(job)
        job_stored = repo._jobs[job_id]
        assert(job_returned == job)
        assert(job_stored == job)

    def test_update_job(self):
        # Test that update replaces job object in entirety
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_initial = {"id": job_id, "parameters": {"height": 3, "width": 4,
                       "depth": 5}}
        job_updated = {"id": job_id, "purple": {"circle": "street",
                       "triangle": "road", "square": "avenue"}}
        repo._jobs[job_id] = job_initial
        job_returned = repo.update_job(job_updated)
        job_stored = repo._jobs[job_id]
        assert(job_returned == job_updated)
        assert(job_stored == job_updated)

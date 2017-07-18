from middleware.job.inmemory_repository import JobRepositoryMemory


class TestJobRepositoryMemory(object):
    # Notes: We use dictionary.get(key) rather than dictionary[key] to ensure
    # we get None rather than KeyError if the key does not exist

    def test_new_repo_has_no_jobs(self):
        repo = JobRepositoryMemory()
        # New repository onject should have empty jobs list
        assert len(repo._jobs) == 0

    def test_exists_for_existing_job_returns_true(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo._jobs[job_id] = job
        job_returned = repo.exists(job_id)
        assert job_returned is True

    def test_exists_for_nonexistent_job_returns_false(self):
        repo = JobRepositoryMemory()
        store_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": store_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo._jobs[store_id] = job
        fetch_id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_returned = repo.exists(fetch_id)
        assert job_returned is False

    def test_exists_for_none_returns_false(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo._jobs[job_id] = job
        job_returned = repo.exists(None)
        assert job_returned is False

    def test_get_existing_job_by_id_returns_job(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo._jobs[job_id] = job
        job_returned = repo.get_by_id(job_id)
        assert job_returned == job

    def test_get_nonexistent_job_by_id_returns_none(self):
        repo = JobRepositoryMemory()
        store_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": store_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo._jobs[store_id] = job
        fetch_id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_returned = repo.get_by_id(fetch_id)
        assert job_returned is None

    def test_create_nonexistent_job_creates_job(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        job_returned = repo.create(job)
        job_stored = repo._jobs.get(job_id)
        assert job_returned == job
        assert job_stored == job

    def test_create_existing_job_returns_none(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_initial = {"id": job_id, "parameters": {"height": 3, "width": 4,
                       "depth": 5}}
        job_updated = {"id": job_id, "purple": {"circle": "street",
                       "triangle": "road", "square": "avenue"}}
        repo._jobs[job_id] = job_initial
        job_returned = repo.create(job_updated)
        job_stored = repo._jobs.get(job_id)
        assert job_returned is None
        assert job_stored is job_initial

    def test_update_replaces_existing_job_completely(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_initial = {"id": job_id, "parameters": {"height": 3, "width": 4,
                       "depth": 5}}
        job_updated = {"id": job_id, "purple": {"circle": "street",
                       "triangle": "road", "square": "avenue"}}
        repo._jobs[job_id] = job_initial
        job_returned = repo.update(job_updated)
        job_stored = repo._jobs.get(job_id)
        assert job_returned == job_updated
        assert job_stored == job_updated

    def test_update_nonexistent_job_returns_none(self):
        repo = JobRepositoryMemory()
        job_id_initial = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_initial = {"id": job_id_initial, "parameters": {"height": 3,
                       "width": 4, "depth": 5}}
        job_id_updated = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_updated = {"id": job_id_updated, "purple": {"circle": "street",
                       "triangle": "road", "square": "avenue"}}
        repo._jobs[job_id_initial] = job_initial
        job_returned = repo.update(job_updated)
        job_stored_updated = repo._jobs.get(job_id_updated)
        job_stored_initial = repo._jobs.get(job_id_initial)
        assert job_returned is None
        assert job_stored_updated is None
        assert job_stored_initial == job_initial

    def test_delete_existing_job_deletes_job(self):
        repo = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        repo._jobs[job_id] = job
        job_returned = repo.delete(job_id)
        job_stored = repo._jobs.get(job_id)
        assert job_returned is None
        assert job_stored is None

    def test_delete_nonexistent_job_returns_none(self):
        repo = JobRepositoryMemory()
        job_id_initial = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_initial = {"id": job_id_initial, "parameters": {"height": 3,
                       "width": 4, "depth": 5}}
        job_id_updated = "ad460823-370c-48dd-a09f-a7564bb458f1"
        repo._jobs[job_id_initial] = job_initial
        job_returned = repo.delete(job_id_updated)
        job_stored = repo._jobs.get(job_id_initial)
        assert job_returned is None
        assert job_stored == job_initial

    def test_list_ids_returns_all_ids(self):
        repo = JobRepositoryMemory()
        # Add multiple jobs to repo
        job_id_1 = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_1 = {"id": job_id_1, "parameters": {"height": 11, "width": 12,
                 "depth": 13}}
        job_id_2 = "53835db6-87cb-4dd8-a91f-5c98100c0b82"
        job_2 = {"id": job_id_2, "parameters": {"height": 21, "width": 22,
                 "depth": 23}}
        job_id_3 = "781692cc-b71c-469e-a8e9-938c2fda89f2"
        job_3 = {"id": job_id_3, "parameters": {"height": 31, "width": 32,
                 "depth": 33}}
        repo._jobs[job_id_1] = job_1
        repo._jobs[job_id_2] = job_2
        repo._jobs[job_id_3] = job_3
        list_expected = [key for key, val in repo._jobs.items()]
        list_returned = repo.list_ids()
        assert list_returned == list_expected

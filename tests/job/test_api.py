from middleware.job.api import JobApi
from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.app import create_app
import unittest
import pytest
from werkzeug.exceptions import NotFound
import json


@pytest.fixture
def test_client(job_repository=JobRepositoryMemory()):
    app = create_app(job_repository)
    return app.test_client()


def response_to_json(response):
    data = response.get_data(as_text=True)
    if not data:
        return None
    return json.loads(data)


class TestJobApi(unittest.TestCase):

    def test_abort_if_not_found_throws_notfound_exception(self):
        jobs = JobRepositoryMemory()
        api = JobApi(job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        with pytest.raises(NotFound):
            api.abort_if_not_found(job_id)

    # === GET tests (READ) ===
    def test_get_for_existing_job_returns_job_with_200_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        jobs.create(job)
        client = test_client(jobs)
        job_response = client.get("/job/{}".format(job_id))
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job

    def test_get_for_nonexistent_job_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.get("/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_get_with_no_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.get("/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    # === PUT tests (UPDATE) ===
    def test_put_with_no_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.put("/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here
        assert len(jobs._jobs) == 0

    def test_put_with_empty_body_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3,
               "width": 4, "depth": 5}}
        jobs.create(job)
        job = None
        client = test_client(jobs)
        job_response = client.put("/job/{}".format(job_id),
                                  data=json.dumps(job),
                                  content_type='application/json')
        error_message = {"message": "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_nonjson_body_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3,
               "width": 4, "depth": 5}}
        jobs.create(job)
        invalid_json = "{key-with-no-value}"
        client = test_client(jobs)
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response handler
        job_response = client.put("/job/{}".format(job_id),
                                  data=invalid_json)
        error_message = {"message": "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_mismatched_job_id_returns_error_with_409_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id_url = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_existing = {"id": job_id_url, "parameters": {"height": 3,
                        "width": 4, "depth": 5}}
        jobs.create(job_existing)
        job_id_json = "59540b31-0454-4875-a00f-94eb4d81a09c"
        job_new = {"id": job_id_json, "parameters": {"blue":
                   "high", "green": "low"}}
        client = test_client(jobs)
        job_response = client.put("/job/{}".format(job_id_url),
                                  data=json.dumps(job_new),
                                  content_type='application/json')
        error_message = {"message": "Job ID in URL ({}) does not match job "
                         "ID in message JSON ({}).".format(job_id_url,
                                                           job_id_json)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_id_url) == job_existing
        assert jobs.get_by_id(job_id_json) is None

    def test_put_with_nonexistent_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.put("/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_put_with_existing_job_id_returns_new_job_with_200_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_original = {"id": job_id, "parameters": {"height": 3,
                        "width": 4, "depth": 5}}
        jobs.create(job_original)
        job_new = {"id": job_id, "parameters": {"blue":
                   "high", "green": "low"}}
        client = test_client(jobs)
        job_response = client.put("/job/{}".format(job_id),
                                  data=json.dumps(job_new),
                                  content_type='application/json')
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_new
        assert jobs.get_by_id(job_id) == job_new

    def test_put_with_invalid_job_json_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3, "width": 4,
               "depth": 5}}
        jobs.create(job)
        client = test_client(jobs)
        invalid_job = {"no-id-field": "valid-json"}
        job_response = client.put("/job/{}".format(job_id),
                                  data=json.dumps(invalid_job),
                                  content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    # === DELETE tests (DELETE) ===
    def test_delete_with_no_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.delete("/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    def test_delete_with_nonexistent_job_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.delete("/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_delete_with_existing_job_id_returns_new_job_with_204_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3, "width": 4,
               "depth": 5}}
        jobs.create(job)
        client = test_client(jobs)
        job_response = client.delete("/job/{}".format(job_id))
        assert job_response.status_code == 204
        assert response_to_json(job_response) is None
        assert jobs.get_by_id(job_id) is None

    # === POST tests (patching) ===
    def test_patch_with_valid_json_and_correct_id(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        job_response_1 = client.post("/job", data=json.dumps(job),
                                     content_type='application/json')

        # complete json with same id as before
        dest_path = 'project/case/'
        template_src = "./middleware/resources/templates/Blue.nml"
        script_src = "./middleware/resources/scripts/start_job.sh"

        job_final = {"id": job_id,
                     "templates": [{"source_uri": template_src,
                                    "destination_path": dest_path}],
                     "scripts": [{"source_uri": script_src,
                                  "destination_path": dest_path}],
                     "parameters": {"viscosity_properties":
                                    {"viscosity_phase_1": 0.09}},
                     "inputs": []}

        job_response_2 = client.post("/job/{}".format(job_id),
                                     data=json.dumps(job_final),
                                     content_type='application/json')

        assert job_response_1.status_code == 200
        assert job_response_2.status_code == 201


class TestJobsApi(object):

    def test_post_for_nonexistent_job_returns_job_with_200_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        client = test_client(jobs)
        job_response = client.post("/job", data=json.dumps(job),
                                   content_type='application/json')
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job
        assert jobs.get_by_id(job_id) == job

    def test_post_for_existing_job_returns_error_with_409_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_existing = {"id": job_id, "parameters": {"height": 3, "width": 4,
                        "depth": 5}}
        jobs.create(job_existing)
        job_new = {"id": job_id, "parameters": {"blue": "high",
                   "green": "low"}}
        client = test_client(jobs)
        job_response = client.post("/job", data=json.dumps(job_new),
                                   content_type='application/json')
        error_message = {"message": "Job with ID {} already "
                         "exists".format(job_id)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_id) == job_existing

    def test_post_with_none_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.post("/job", data=json.dumps(None),
                                   content_type='application/json')
        error_message = {"message": "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message
        assert len(jobs._jobs) == 0

    def test_post_with_nonjson_body_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        invalid_json = "{key-with-no-value}"
        client = test_client(jobs)
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response handler
        job_response = client.post("/job", data=invalid_json)
        error_message = {"message": "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_post_with_invalid_job_json_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        invalid_job = {"no-id-field": "valid-json"}
        client = test_client(jobs)
        job_response = client.post("/job", data=json.dumps(invalid_job),
                                   content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

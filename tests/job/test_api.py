import json
import pytest
import unittest
import unittest.mock as mock
from werkzeug.exceptions import NotFound
from middleware.job.api import JobApi
from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.factory import create_app


@pytest.fixture
def test_client(job_repository=JobRepositoryMemory()):
    app = create_app(job_repository)
    return app.test_client()


@pytest.fixture(autouse=True)
def app_config(monkeypatch):
    monkeypatch.setenv('APP_CONFIG_FILE', '../config/travis.py')


def mock_run_remote(script_name, remote_path, debug=True):
    return script_name, 'err', '0'


def mock_patch_all():
    return True


def mock_transfer_all():
    return True


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
        job_response = client.get("/api/job/{}".format(job_id))
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job

    def test_get_for_nonexistent_job_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.get("/api/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_get_with_no_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.get("/api/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    # === PUT tests (UPDATE) ===
    def test_put_with_no_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.put("/api/job/")
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
        job_response = client.put("/api/job/{}".format(job_id),
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
        job_response = client.put("/api/job/{}".format(job_id),
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
        job_response = client.put("/api/job/{}".format(job_id_url),
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
        job_response = client.put("/api/job/{}".format(job_id))
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
        job_response = client.put("/api/job/{}".format(job_id),
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
        job_response = client.put("/api/job/{}".format(job_id),
                                  data=json.dumps(invalid_job),
                                  content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    # === DELETE tests (DELETE) ===
    def test_delete_with_no_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.delete("/api/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    def test_delete_with_nonexistent_job_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.delete("/api/job/{}".format(job_id))
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
        job_response = client.delete("/api/job/{}".format(job_id))
        assert job_response.status_code == 204
        assert response_to_json(job_response) is None
        assert jobs.get_by_id(job_id) is None

    # === POST tests  ===
    def test_post_with_valid_json_correct_id_returns_new_job_success_200(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/job/{}".format(job_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        assert response_to_json(job_response) == job
        assert job_response.status_code == 200

    def test_post_with_valid_json_and_incorrect_id_returns_error_404(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job = {"id": job_id[::-1], "parameters": {"height": 3}}

        job_response = client.post("/api/job/{}".format(job_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        error_message = {"message": "Job {} not found".format(job_id[::-1])}

        assert response_to_json(job_response) == error_message
        assert job_response.status_code == 404

    def test_post_with_missing_json_returns_error_400(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/job/{}".format(job_id),
                                   data=None,
                                   content_type=None)

        error_message = {"message": "Message body could not be parsed as JSON"}

        assert response_to_json(job_response) == error_message
        assert job_response.status_code == 400

    def test_post_with_invalid_json_returns_error_400(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        broken_json = {'test': 5}

        job_response = client.post("/api/job/{}".format(job_id),
                                   data=json.dumps(broken_json),
                                   content_type='application/json')

        error_message = {"message": "Message body is not valid Job JSON"}

        assert response_to_json(job_response) == error_message
        assert job_response.status_code == 400

    # === PATCH tests (Partial UPDATE) ===
    def test_patch_with_no_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.patch("/api/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here
        assert len(jobs._jobs) == 0

    def test_patch_with_empty_body_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3,
               "width": 4, "depth": 5}}
        jobs.create(job)
        job = None
        client = test_client(jobs)
        job_response = client.patch("/api/job/{}".format(job_id),
                                    data=json.dumps(job),
                                    content_type='application/json-patch+json')
        error_message = {"message": "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_patch_with_nonjson_body_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3,
               "width": 4, "depth": 5}}
        jobs.create(job)
        invalid_json = "{key-with-no-value}"
        client = test_client(jobs)
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response handler
        job_response = client.patch("/api/job/{}".format(job_id),
                                    data=invalid_json)
        error_message = {"message": "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_patch_with_nonexistent_job_id_returns_error_with_404_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.patch("/api/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_patch_with_mismatched_job_id_returns_error_with_409_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id_url = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_existing = {"id": job_id_url, "parameters": {"height": 3,
                        "width": 4, "depth": 5}}
        jobs.create(job_existing)
        job_id_json = "59540b31-0454-4875-a00f-94eb4d81a09c"
        job_new = {"id": job_id_json, "parameters": {"height":
                   7, "green": "low", "depth": None}}
        client = test_client(jobs)
        job_response = client.patch(
                        "/api/job/{}".format(job_id_url),
                        data=json.dumps(job_new),
                        content_type='application/merge-patch+json')
        error_message = {"message": "Job ID in URL ({}) does not match job "
                         "ID in message JSON ({}).".format(job_id_url,
                                                           job_id_json)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_id_url) == job_existing
        assert jobs.get_by_id(job_id_json) is None

    def test_patch_with_existing_job_id_returns_new_job_with_200_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_original = {"id": job_id, "parameters": {"height": 3,
                        "width": 4, "depth": 5}}
        jobs.create(job_original)
        job_patch = {"parameters": {"height":
                     7, "green": "low", "depth": None}}
        job_new_expected = {"id": job_id, "parameters": {"height": 7,
                            "width": 4, "green": "low"}}
        client = test_client(jobs)
        job_response = client.patch(
                        "/api/job/{}".format(job_id),
                        data=json.dumps(job_patch),
                        content_type='application/merge-patch+json')
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_new_expected
        assert jobs.get_by_id(job_id) == job_new_expected


class TestRunApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'patch_all_templates', side_effect=mock_patch_all)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'transfer_all_files', side_effect=mock_transfer_all)
    def test_run_with_valid_id(self, mock_transfer, mock_patch, mock_run):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create full job
        job = {
            "id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "templates": [
                {
                    "source_uri": "./resources/templates/Blue.nml",
                    "destination_path": "project/case/"
                }
            ],
            "scripts": [
                {"source_uri": "./resources/scripts/start_job.sh",
                 "destination_path": "project/case/", "action": "RUN"},
                {"source_uri": "./resources/scripts/cancel_job.sh",
                 "destination_path": "project/case/", "action": "CANCEL"},
                {"source_uri": "./resources/scripts/progress_job.sh",
                 "destination_path": "project/case/", "action": "PROGRESS"},
                {"source_uri": "./resources/scripts/setup_job.sh",
                 "destination_path": "project/case/", "action": "SETUP"}
            ],
            "parameters": {
                "viscosity_properties": {
                    "viscosity_phase_1": "42.0"
                }
            },
            "inputs": []
        }

        job_id = job['id']

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/run/{}".format(job_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'start_job.sh'
        assert job_response.status_code == 200

    def test_run_with_invalid_id(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("/api/run/{}".format(bad_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/run/{0}] but did'
                                   ' you mean /api/run/<string:job_id> '
                                   '?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404

    def test_run_with_no_json(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/run/{}".format(job_id))

        err_message = {'message': ('Message body could not be parsed as JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400

    def test_run_with_invalid_json(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        broken_json = {'test': 5}

        job_response = client.post("/api/run/{}".format(job_id),
                                   data=json.dumps(broken_json),
                                   content_type='application/json')

        err_message = {'message': ('Message body is not valid Job JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400


class TestSetupApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'patch_all_templates', side_effect=mock_patch_all)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'transfer_all_files', side_effect=mock_transfer_all)
    def test_setup_with_valid_id(self, mock_transfer, mock_patch, mock_run):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create full job
        job = {
            "id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "templates": [
                {
                    "source_uri": "./resources/templates/Blue.nml",
                    "destination_path": "project/case/"
                }
            ],
            "scripts": [
                {"source_uri": "./resources/scripts/start_job.sh",
                 "destination_path": "project/case/", "action": "RUN"},
                {"source_uri": "./resources/scripts/cancel_job.sh",
                 "destination_path": "project/case/", "action": "CANCEL"},
                {"source_uri": "./resources/scripts/progress_job.sh",
                 "destination_path": "project/case/", "action": "PROGRESS"},
                {"source_uri": "./resources/scripts/setup_job.sh",
                 "destination_path": "project/case/", "action": "SETUP"}
            ],
            "parameters": {
                "viscosity_properties": {
                    "viscosity_phase_1": "42.0"
                }
            },
            "inputs": []
        }

        job_id = job['id']

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/setup/{}".format(job_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'setup_job.sh'
        assert job_response.status_code == 200

    def test_setup_with_invalid_id(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("/api/setup/{}".format(bad_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/setup/{0}] but did '
                                   'you mean /api/setup/<string:job_id> or '
                                   '/api/run/<string:job_id> '
                                   '?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404

    def test_setup_with_no_json(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/setup/{}".format(job_id))

        err_message = {'message': ('Message body could not be parsed as JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400

    def test_setup_with_invalid_json(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        broken_json = {'test': 5}

        job_response = client.post("/api/setup/{}".format(job_id),
                                   data=json.dumps(broken_json),
                                   content_type='application/json')

        err_message = {'message': ('Message body is not valid Job JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400


class TestCancelApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_cancel_with_valid_id(self, mock_run):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create full job
        job = {
            "id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "templates": [
                {
                    "source_uri": "./resources/templates/Blue.nml",
                    "destination_path": "project/case/"
                }
            ],
            "scripts": [
                {"source_uri": "./resources/scripts/start_job.sh",
                 "destination_path": "project/case/", "action": "RUN"},
                {"source_uri": "./resources/scripts/cancel_job.sh",
                 "destination_path": "project/case/", "action": "CANCEL"},
                {"source_uri": "./resources/scripts/progress_job.sh",
                 "destination_path": "project/case/", "action": "PROGRESS"},
                {"source_uri": "./resources/scripts/setup_job.sh",
                 "destination_path": "project/case/", "action": "SETUP"}
            ],
            "parameters": {
                "viscosity_properties": {
                    "viscosity_phase_1": "42.0"
                }
            },
            "inputs": []
        }

        job_id = job['id']

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/cancel/{}".format(job_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'cancel_job.sh'
        assert job_response.status_code == 200

    def test_cancel_with_invalid_id(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("/api/cancel/{}".format(bad_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/cancel/{0}] but did '
                                   'you mean /api/cancel/<string:job_id> '
                                   '?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404


class TestProgressApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_progress_with_valid_id(self, mock_run):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create full job
        job = {
            "id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "templates": [
                {
                    "source_uri": "./resources/templates/Blue.nml",
                    "destination_path": "project/case/"
                }
            ],
            "scripts": [
                {"source_uri": "./resources/scripts/start_job.sh",
                 "destination_path": "project/case/", "action": "RUN"},
                {"source_uri": "./resources/scripts/cancel_job.sh",
                 "destination_path": "project/case/", "action": "CANCEL"},
                {"source_uri": "./resources/scripts/progress_job.sh",
                 "destination_path": "project/case/", "action": "PROGRESS"},
                {"source_uri": "./resources/scripts/setup_job.sh",
                 "destination_path": "project/case/", "action": "SETUP"}
            ],
            "parameters": {
                "viscosity_properties": {
                    "viscosity_phase_1": "42.0"
                }
            },
            "inputs": []
        }

        job_id = job['id']

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        job_response = client.post("/api/progress/{}".format(job_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'progress_job.sh'
        assert job_response.status_code == 200

    def test_cancel_with_invalid_id(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)

        # Create skeleton job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id, "parameters": {"height": 3}}

        _ = client.post("/api/job", data=json.dumps(job),
                        content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("/api/progress/{}".format(bad_id),
                                   data=json.dumps(job),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/progress/{0}] but did '
                                   'you mean /api/progress/'
                                   '<string:job_id> ?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404


class TestJobsApi(object):

    # === GET tests (LIST) ===
    def test_get_returns_object_summary_list(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id_1 = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_1 = {"id": job_id_1, "parameters": {"height": 11, "width": 12,
                 "depth": 13}}
        job_id_2 = "53835db6-87cb-4dd8-a91f-5c98100c0b82"
        job_2 = {"id": job_id_2, "parameters": {"height": 21, "width": 22,
                 "depth": 23}}
        job_id_3 = "781692cc-b71c-469e-a8e9-938c2fda89f2"
        job_3 = {"id": job_id_3, "parameters": {"height": 31, "width": 32,
                 "depth": 33}}
        jobs.create(job_1)
        jobs.create(job_2)
        jobs.create(job_3)
        client = test_client(jobs)

        def job_uri(job_id):
            return "/api/job/{}".format(job_id)

        expected_response = [{"id": job_id_1, "uri": job_uri(job_id_1)},
                             {"id": job_id_2, "uri": job_uri(job_id_2)},
                             {"id": job_id_3, "uri": job_uri(job_id_3)}]
        job_response = client.get("/api/job")
        assert job_response.status_code == 200
        # Both lists of dictionaries need to have same sort order to
        # successfully compare
        assert response_to_json(job_response).sort(key=lambda x: x["id"]) == \
            expected_response.sort(key=lambda x: x["id"])

    # === POST tests (CREATE) ===
    def test_post_for_nonexistent_job_returns_job_with_200_status(self):
        jobs = JobRepositoryMemory()
        # Create job
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job = {"id": job_id,
               "parameters": {"height": 3, "width": 4, "depth": 5}}
        client = test_client(jobs)
        job_response = client.post("/api/job", data=json.dumps(job),
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
        job_response = client.post("/api/job", data=json.dumps(job_new),
                                   content_type='application/json')
        error_message = {"message": "Job with ID {} already "
                         "exists".format(job_id)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_id) == job_existing

    def test_post_with_none_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        client = test_client(jobs)
        job_response = client.post("/api/job", data=json.dumps(None),
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
        job_response = client.post("/api/job", data=invalid_json)
        error_message = {"message": "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_post_with_invalid_job_json_returns_error_with_400_status(self):
        jobs = JobRepositoryMemory()
        invalid_job = {"no-id-field": "valid-json"}
        client = test_client(jobs)
        job_response = client.post("/api/job", data=json.dumps(invalid_job),
                                   content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

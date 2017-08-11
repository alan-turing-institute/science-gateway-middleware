import json
import pytest
from flask import Flask
import unittest.mock as mock
from werkzeug.exceptions import NotFound
from middleware.factory import create_app
from middleware.job.api import JobApi
from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.database import db as _db
from middleware.job.models import Job, Parameter, Template, Script, Input
from middleware.job.schema import job_to_json
from new_jobs import new_job1, new_job2, new_job3, new_job4

CONFIG_NAME = "test"
TEST_DB_URI = 'sqlite://'


@pytest.fixture
def test_client(job_repository=JobRepositoryMemory()):
    app = create_app(CONFIG_NAME, job_repository)
    return app.test_client()


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test Flask app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.test")
    _db.init_app(app)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database"""
    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Function-wide SQLAlchemy session for each test"""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={}, expire_on_commit=True)
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


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


def mock_api_post(job_id):
    return {"std out": [job_id], "std err": [job_id]}, 201


class TestJobApi(object):

    def test_abort_if_not_found_throws_notfound_exception(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        api = JobApi(job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        with pytest.raises(NotFound):
            api.abort_if_not_found(job_id)

    # === GET tests (READ) ===
    def test_get_for_existing_job_returns_job_with_200(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)

        job1 = new_job1()  # create a job object
        job1_id = job1.id  # extract its id
        job1_json = job_to_json(job1)  # store json representation

        # add job to the database via the api
        jobs.create(job1)

        # query the database via the api
        job_response = client.get("/api/job/{}".format(job1_id))

        assert job_response.status_code == 200
        assert response_to_json(job_response) == job1_json

    def test_get_for_nonexistent_job_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.get("/api/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_get_with_no_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.get("/api/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    # === PUT tests (UPDATE) ===
    def test_put_with_no_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.put("/api/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here
        assert len(jobs.list_ids()) == 0

    def test_put_with_empty_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        job = new_job1()
        jobs.create(job)
        job_query = None
        client = test_client(jobs)
        job_response = client.put("/api/job/{}".format(job.id),
                                  data=json.dumps(job_query),
                                  content_type='application/json')
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_nonjson_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        job = new_job1()
        jobs.create(job)
        invalid_json = "{key-with-no-value}"
        client = test_client(jobs)
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response
        # handler
        job_response = client.put("/api/job/{}".format(job.id),
                                  data=invalid_json)
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_mismatched_job_id_returns_error_with_409(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        job_existing = new_job1()
        jobs.create(job_existing)
        client = test_client(jobs)
        # Use first job ID for URL, but provide a second, new job in JSON body
        job_id_url = job_existing.id
        job_new = new_job2()
        job_json = job_new
        job_id_json = job_json.id
        job_response = client.put("/api/job/{}".format(job_id_url),
                                  data=json.dumps(job_to_json(job_json)),
                                  content_type='application/json')
        job_existing == job_existing
        error_message = {"message": "Job ID in URL ({}) does not match job "
                         "ID in message JSON ({}).".format(job_id_url,
                                                           job_id_json)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_id_url) == job_existing
        assert jobs.get_by_id(job_id_json) is None

    def test_put_with_nonexistent_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.put("/api/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_put_with_existing_job_id_returns_new_job_with_200(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job_original = new_job1()
        job_id_orig = job_original.id
        jobs.create(job_original)
        job_new = new_job2()
        job_new.id = job_id_orig
        client = test_client(jobs)
        job_response = client.put("/api/job/{}".format(job_id_orig),
                                  data=json.dumps(job_to_json(job_new)),
                                  content_type='application/json')
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_to_json(job_new)
        assert jobs.get_by_id(job_id_orig) == job_new

    def test_put_with_no_id_in_json_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job_orig = new_job1()
        job_id_orig = job_orig.id
        jobs.create(job_orig)
        client = test_client(jobs)
        invalid_job = {"no-id-field": "valid-json"}
        job_response = client.put("/api/job/{}".format(job_id_orig),
                                  data=json.dumps(invalid_job),
                                  content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_invalid_job_json_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job_orig = new_job1()
        job_id_orig = job_orig.id
        jobs.create(job_orig)
        client = test_client(jobs)
        invalid_job_json = {"id": job_id_orig, "invalid-name": "valid-value"}
        job_response = client.put("/api/job/{}".format(job_id_orig),
                                  data=json.dumps(invalid_job_json),
                                  content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    # === DELETE tests (DELETE) ===
    def test_delete_with_no_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.delete("/api/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    def test_delete_with_nonexistent_job_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.delete("/api/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_delete_for_existing_job_id_returns_none_with_204(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job_orig = new_job1()
        job_id_orig = job_orig.id
        jobs.create(job_orig)
        client = test_client(jobs)

        job_response = client.delete("/api/job/{}".format(job_id_orig))
        assert job_response.status_code == 204
        assert response_to_json(job_response) is None
        assert jobs.get_by_id(job_id_orig) is None

    # === PATCH tests (Partial UPDATE) ===
    def test_patch_with_no_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.patch("/api/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here
        assert len(jobs.list_ids()) == 0

    def test_patch_with_empty_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        job = new_job1()
        jobs.create(job)
        job_id = job.id
        job = None
        client = test_client(jobs)
        job_response = client.patch("/api/job/{}".format(job_id),
                                    data=json.dumps(job),
                                    content_type='application/json-patch+json')
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_patch_with_nonjson_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        job = new_job1()
        jobs.create(job)
        job_id = job.id
        invalid_json = "{key-with-no-value}"
        client = test_client(jobs)
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response
        # handler
        job_response = client.patch("/api/job/{}".format(job_id),
                                    data=invalid_json)
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_patch_for_nonexistent_job_id_gives_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.patch("/api/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_patch_with_mismatched_job_id_gives_error_with_409(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job_existing = new_job1()
        jobs.create(job_existing)
        job_id_url = job_existing.id
        job_new = new_job2()
        job_id_json = job_new.id
        client = test_client(jobs)
        job_response = client.patch(
            "/api/job/{}".format(job_id_url),
            data=json.dumps(job_to_json(job_new)),
            content_type='application/merge-patch+json')
        error_message = {"message": "Job ID in URL ({}) does not match job "
                         "ID in message JSON ({}).".format(job_id_url,
                                                           job_id_json)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_id_url) == job_existing
        assert jobs.get_by_id(job_id_json) is None

    def test_patch_with_existing_job_id_gives_new_job_with_200(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job_original = new_job1()
        jobs.create(job_original)
        added_param = {"name": "j1p3name", "value": "added_value"}
        changed_param = {"name": "j1p1name", "value": "changed_value"}
        deleted_param = {"name": "j1p2name", "value": None}
        job_patch_json = {"id": job_original.id,
                          "parameters": [added_param, changed_param]}
        client = test_client(jobs)
        job_response = client.patch(
            "/api/job/{}".format(job_original.id),
            data=json.dumps(job_patch_json),
            content_type='application/merge-patch+json')
        # Construct expected Job object by manually applying changes
        job_expected = new_job1()
        job_expected.id = job_original.id
        # Append new parameter
        job_expected.parameters.append(
            Parameter(name=added_param.get("name"),
                      value=added_param.get("value")))
        # Replace changed parameter
        job_expected.parameters = [
            Parameter(name=changed_param.get("name"),
                      value=changed_param.get("value")) if
            p.name == changed_param.get("name") else p for p in
            job_expected.parameters]
        # Remove deleted parameter
        job_expected.parameters = [p for p in job_expected.parameters if
                                   p.name != deleted_param.get("name")]
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_to_json(job_expected)
        assert jobs.get_by_id(job_original.id) == job_expected


class TestJobsApi(object):

    # === GET tests (LIST) ===
    def test_get_returns_object_summary_list(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job1 = new_job1()
        job2 = new_job2()
        job3 = new_job3()
        jobs.create(job1)
        jobs.create(job2)
        jobs.create(job3)
        client = test_client(jobs)

        def job_uri(job_id):
            return "/api/job/{}".format(job_id)

        expected_response = [{"id": job1.id, "uri": job_uri(job1.id)},
                             {"id": job2.id, "uri": job_uri(job2.id)},
                             {"id": job3.id, "uri": job_uri(job3.id)}]
        job_response = client.get("/api/job")
        assert job_response.status_code == 200
        # Both lists of dictionaries need to have same sort order to
        # successfully compare
        assert response_to_json(job_response).sort(key=lambda x: x["id"]) ==\
            expected_response.sort(key=lambda x: x["id"])

    # === POST tests (CREATE) ===
    def test_post_for_nonexistent_job_returns_job_with_200(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job = new_job1()
        client = test_client(jobs)
        job_response = client.post("/api/job",
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_to_json(job)
        assert jobs.get_by_id(job.id) == job

    def test_post_for_existing_job_returns_error_with_409(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create and store job
        job_existing = new_job1()
        jobs.create(job_existing)
        # Try and create a new job with the same ID
        job_new = new_job2()
        job_new.id = job_existing.id
        client = test_client(jobs)
        job_response = client.post("/api/job",
                                   data=json.dumps(job_to_json(job_new)),
                                   content_type='application/json')
        error_message = {"message": "Job with ID {} already "
                         "exists".format(job_existing.id)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_existing.id) == job_existing

    def test_post_with_none_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.post("/api/job", data=json.dumps(None),
                                   content_type='application/json')
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message
        assert len(jobs.list_ids()) == 0

    def test_post_with_nonjson_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        invalid_json = "{key-with-no-value}"
        client = test_client(jobs)
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response
        # handler
        job_response = client.post("/api/job", data=invalid_json)
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message
        assert len(jobs.list_ids()) == 0

    def test_post_with_invalid_job_json_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        invalid_job = {"no-id-field": "valid-json"}
        client = test_client(jobs)
        job_response = client.post("/api/job", data=json.dumps(invalid_job),
                                   content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message
        assert len(jobs.list_ids()) == 0


class TestRunApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'patch_all_templates', side_effect=mock_patch_all)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'transfer_all_files', side_effect=mock_transfer_all)
    def test_run_with_valid_id(self, mock_tr, mock_patch, mock_run, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("/api/run/{}".format(job_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'j4s1source'
        assert job_response.status_code == 200

    def test_run_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("/api/run/{}".format(bad_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/run/{0}] but did you mean '
                                   '/api/run/<string:job_id>'
                                   ' ?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404

    def test_run_with_no_json(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("/api/run/{}".format(job_id))

        err_message = {'message': ('Message body could not be parsed as JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400

    def test_run_with_invalid_json(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        broken_json = {'test': 5}

        job_response = client.post("/api/run/{}".format(job_id),
                                   data=json.dumps(broken_json),
                                   content_type='application/json')

        err_message = {'message': 'No ID found in Job JSON'}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400


class TestSetupApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'patch_all_templates', side_effect=mock_patch_all)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'transfer_all_files', side_effect=mock_transfer_all)
    def test_setup_with_valid_id(self, mock_tr, mock_patch, mock_run, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("/api/setup/{}".format(job_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'j4s4source'
        assert job_response.status_code == 200

    def test_setup_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2si3"

        job_response = client.post("/api/setup/{}".format(bad_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/setup/{0}] but did you '
                                   'mean /api/setup/<string:job_id>'
                                   ' ?').format(bad_id)}
        # print(response_to_json(job_response))
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404

    def test_setup_with_no_json(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("/api/setup/{}".format(job_id))

        err_message = {'message': ('Message body could not be parsed as JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400

    def test_setup_with_invalid_json(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        broken_json = {'test': 5}

        job_response = client.post("/api/setup/{}".format(job_id),
                                   data=json.dumps(broken_json),
                                   content_type='application/json')

        err_message = {'message': 'No ID found in Job JSON'}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400


class TestCancelApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_cancel_with_valid_id(self, mock_run, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("/api/cancel/{}".format(job_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'j4s3source'
        assert job_response.status_code == 200

    def test_cancel_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("/api/cancel/{}".format(bad_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/cancel/{0}] but did '
                                   'you mean /api/cancel/'
                                   '<string:job_id> ?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404


class TestProgressApi(object):

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_progress_with_valid_id(self, mock_run, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("/api/progress/{}".format(job_id))

        assert response_to_json(job_response)['stdout'] == 'j4s2source'
        assert job_response.status_code == 200

    def test_progress_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)

        job = new_job4()
        client = test_client(jobs)

        job_id = job.id

        client.post("/api/job", data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("/api/progress/{}".format(bad_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/progress/{0}] but did '
                                   'you mean /api/progress/'
                                   '<string:job_id> ?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404


class TestTemplateApi(object):

    def test_get_template_valid_request(self):

        client = test_client()
        valid_json = '{"case": "./resources/cases/case1.json"}'

        response = client.get("api/template/", data=valid_json,
                              content_type='application/json')

        # NOT TESTING AGAINST TEMPLATE CONTENTS AS WE DONT KNOW THE
        # FINAL FORMAT YET. TODO: FIX THIS!
        assert response.status_code == 200

    def test_get_template_invalid_json(self):
        client = test_client()
        invalid_json = '{"incorrect_key": "./resources/cases/case1.json"}'

        response = client.get("api/template/", data=invalid_json,
                              content_type='application/json')

        err_message = {'message': 'Message body is not valid case JSON'}

        assert response.status_code == 400
        assert response_to_json(response) == err_message

    def test_get_template_no_json(self):
        client = test_client()

        response = client.get("api/template/")
        err_message = {'message': 'Message body could not be parsed as JSON'}

        assert response.status_code == 400
        assert response_to_json(response) == err_message

    def test_get_template_missing_template_file(self):
        client = test_client()
        missing_file_json = '{"case": "./resources/cases/case_missing.json"}'
        response = client.get("api/template/", data=missing_file_json,
                              content_type='application/json')

        assert response.status_code == 404

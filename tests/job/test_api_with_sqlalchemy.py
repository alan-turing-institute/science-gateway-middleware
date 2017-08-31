import os
import json
import pytest
from flask import Flask
import arrow
import unittest.mock as mock
from werkzeug.exceptions import NotFound
from middleware.factory import create_app
from middleware.job.api import JobApi, CaseApi, CasesApi
from middleware.job.sqlalchemy_repository import (
    JobRepositorySqlAlchemy, CaseRepositorySqlAlchemy)
from middleware.database import db as _db
from middleware.job.models import Job, Parameter, Template, Script, Input
from middleware.job.schema import job_to_json
from middleware.factory import json_to_case_list
import new_jobs as nj  # for easy access to iso_string values
from new_jobs import (new_job1, new_job2, new_job3, new_job4,
                      new_case1, new_job1_output_json)
from config.base import MIDDLEWARE_URL, URI_STEMS
import json

CONFIG_NAME = "test"
TEST_DB_URI = 'sqlite://'
CASES_JSON_FILENAME = './resources/cases/blue_cases.json'


@pytest.fixture
def test_client(case_repository=None,
                job_repository=None):
    app = create_app(CONFIG_NAME, case_repository, job_repository)
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


def mock_run_remote(
        script_name, remote_path, debug=True):
    return script_name, 'err', '0'


def mock_run_remote_return_json(
        script_name, remote_path, debug=True):
    out = json.dumps({"name": script_name})
    return out, 'err', '0'


def mock_patch_all():
    return True


def mock_transfer_all():
    return True


def mock_create_job_directory():
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
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job1 = new_job1()  # create a job object
        job1_id = job1.id  # extract its id
        job1_json = job_to_json(job1)  # store json representation

        # add job to the database via the api
        jobs.create(job1)

        # query the database via the api
        job_response = client.get("{}/{}".format(URI_STEMS['jobs'], job1_id))

        assert job_response.status_code == 200
        assert response_to_json(job_response) == job1_json

    def test_get_for_nonexistent_job_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.get("{}/{}".format(URI_STEMS['jobs'], job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    # === PUT tests (UPDATE) ===
    def test_put_with_no_job_id_returns_error_with_405(self, session):
        # With no job_id, this attempts to call JobsApi, which does not
        # have a put method
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_response = client.put(URI_STEMS['jobs'])
        assert job_response.status_code == 405
        assert len(jobs.list_ids()) == 0

    def test_put_with_empty_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job = new_job1()
        jobs.create(job)
        job_query = None
        client = test_client(cases, jobs)
        job_response = client.put("{}/{}".format(URI_STEMS['jobs'], job.id),
                                  data=json.dumps(job_query),
                                  content_type='application/json')
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_nonjson_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job = new_job1()
        jobs.create(job)
        invalid_json = "{key-with-no-value}"
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response
        # handler
        job_response = client.put("{}/{}".format(URI_STEMS['jobs'], job.id),
                                  data=invalid_json)
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_mismatched_job_id_returns_error_with_409(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_existing = new_job1()
        jobs.create(job_existing)
        # Use first job ID for URL, but provide a second, new job in JSON body
        job_id_url = job_existing.id
        job_new = new_job2()
        job_json = job_new
        job_id_json = job_json.id
        job_response = client.put("{}/{}".format(URI_STEMS['jobs'], job_id_url),
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
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.put("{}/{}".format(URI_STEMS['jobs'], job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_put_with_existing_job_id_returns_new_job_with_200(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        # Create job
        job_original = new_job1()
        job_id_orig = job_original.id
        jobs.create(job_original)

        job_new = new_job2()
        job_new.id = job_id_orig

        job_response = client.put(
            "{}/{}".format(URI_STEMS['jobs'], job_id_orig),
            data=json.dumps(job_to_json(job_new)),
            content_type='application/json')

        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_to_json(job_new)
        assert jobs.get_by_id(job_id_orig) == job_new

    def test_put_with_no_id_in_json_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        # Create job
        job_orig = new_job1()
        job_id_orig = job_orig.id
        jobs.create(job_orig)

        invalid_job = {"no-id-field": "valid-json"}
        job_response = client.put("{}/{}".format(URI_STEMS['jobs'], job_id_orig),
                                  data=json.dumps(invalid_job),
                                  content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_put_with_invalid_job_json_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        # Create job
        job_orig = new_job1()
        job_id_orig = job_orig.id
        jobs.create(job_orig)

        invalid_job_json = {"id": job_id_orig, "invalid-name": "valid-value"}
        job_response = client.put("{}/{}".format(URI_STEMS['jobs'], job_id_orig),
                                  data=json.dumps(invalid_job_json),
                                  content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    # === DELETE tests (DELETE) ===
    def test_delete_with_no_job_id_returns_error_with_405(self, session):
        # With no job_id, this attempts to call JobsApi, which does not
        # have a delete method
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_response = client.delete(URI_STEMS['jobs'])
        assert job_response.status_code == 405

    def test_delete_with_nonexistent_job_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.delete("{}/{}".format(URI_STEMS['jobs'], job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_delete_for_existing_job_id_returns_none_with_204(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        # Create job
        job_orig = new_job1()
        job_id_orig = job_orig.id
        jobs.create(job_orig)

        job_response = client.delete("{}/{}".format(URI_STEMS['jobs'],
                                                   job_id_orig))
        assert job_response.status_code == 204
        assert response_to_json(job_response) is None
        assert jobs.get_by_id(job_id_orig) is None

    # === PATCH tests (Partial UPDATE) ===
    def test_patch_with_no_job_id_returns_error_with_405(self, session):
        # With no job_id, this attempts to call JobsApi, which does not
        # have a patch method
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_response = client.patch(URI_STEMS['jobs'])
        assert job_response.status_code == 405
        assert len(jobs.list_ids()) == 0

    def test_patch_with_empty_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job = new_job1()
        jobs.create(job)
        job_id = job.id
        job = None
        job_response = client.patch("{}/{}".format(URI_STEMS['jobs'], job_id),
                                    data=json.dumps(job),
                                    content_type='application/json-patch+json')
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_patch_with_nonjson_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job = new_job1()
        jobs.create(job)
        job_id = job.id
        invalid_json = "{key-with-no-value}"
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response
        # handler
        job_response = client.patch("{}/{}".format(URI_STEMS['jobs'], job_id),
                                    data=invalid_json)
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    def test_patch_for_nonexistent_job_id_gives_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.patch("{}/{}".format(URI_STEMS['jobs'], job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_patch_with_mismatched_job_id_gives_error_with_409(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        # Create job
        job_existing = new_job1()
        jobs.create(job_existing)
        job_id_url = job_existing.id
        job_new = new_job2()
        job_id_json = job_new.id
        job_response = client.patch(
            "{}/{}".format(URI_STEMS['jobs'], job_id_url),
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
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        # Create job
        job_original = new_job1()
        _created = jobs.create(job_original)

        j1f1p1_changed_param = {
                "help": "j1f1p1help",
                "label": "j1f1p1label",
                "min_value": "j1f1p1min_value",
                "max_value": "j1f1p1max_value",
                "name": "j1f1p1name",
                "type": "j1f1p1type",
                "type_value": "j1f1p1type_value",
                "units": "j1f1p1units",
                "value": "changed_value"
            }

        j1f1p3_added_param = {
                "help": "j1f1p3help",
                "label": "j1f1p3label",
                "min_value": "j1f1p3min_value",
                "max_value": "j1f1p3max_value",
                "name": "j1f1p3name",
                "type": "j1f1p3type",
                "type_value": "j1f1p3type_value",
                "units": "j1f1p3units",
                "value": "added_value"
            }

        # here we must supply an entire families array
        # as json merge-patch cannot be used to update
        # non-objects
        # NOTE: the action of this patch is to remove
        # the parameter j1f1p2
        job_patch_json = {
                "id": job_original.id,
                "families": [
                    {
                        "name": "j1f1name",
                        "label": "j1f1label",
                        "collapse": True,
                        "parameters": [
                            j1f1p1_changed_param,
                            j1f1p3_added_param
                        ]
                    }
                ]
            }

        job_response = client.patch(
            "{}/{}".format(URI_STEMS['jobs'], job_original.id),
            data=json.dumps(job_patch_json),
            content_type='application/merge-patch+json')

        # Construct expected Job object by manually applying changes
        job_expected = new_job1()
        job_expected.id = job_original.id
        job_expected.families[0].parameters[0].help = "j1f1p1help"
        job_expected.families[0].parameters[0].label = "j1f1p1label"
        job_expected.families[0].parameters[0].min_value = \
            "j1f1p1min_value"
        job_expected.families[0].parameters[0].max_value = \
            "j1f1p1max_value"
        job_expected.families[0].parameters[0].name = "j1f1p1name"
        job_expected.families[0].parameters[0].type = "j1f1p1type"
        job_expected.families[0].parameters[0].type_value = \
            "j1f1p1type_value"
        job_expected.families[0].parameters[0].units = "j1f1p1units"
        job_expected.families[0].parameters[0].value = "changed_value"

        job_expected.families[0].parameters[1].help = "j1f1p3help"
        job_expected.families[0].parameters[1].label = "j1f1p3label"
        job_expected.families[0].parameters[1].min_value = \
            "j1f1p3min_value"
        job_expected.families[0].parameters[1].max_value = \
            "j1f1p3max_value"
        job_expected.families[0].parameters[1].name = "j1f1p3name"
        job_expected.families[0].parameters[1].type = "j1f1p3type"
        job_expected.families[0].parameters[1].type_value = \
            "j1f1p3type_value"
        job_expected.families[0].parameters[1].units = "j1f1p3units"
        job_expected.families[0].parameters[1].value = "added_value"

        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_to_json(job_expected)
        assert jobs.get_by_id(job_original.id) == job_expected


class TestJobsApi(object):

    # === GET tests (LIST) ===
    def test_get_returns_object_summary_list(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        # Create job
        job1 = new_job1()
        job2 = new_job2()
        job3 = new_job3()
        jobs.create(job1)
        jobs.create(job2)
        jobs.create(job3)

        expected_response = {"jobs": [
            {
                "id": job1.id,
                "uri": job1.uri,
                "status": job1.status,
                "name": job1.name,
                "description": job1.description,
                "creation_datetime": nj.j1c_iso_string,
                "start_datetime": nj.j1s_iso_string,
                "end_datetime": nj.j1e_iso_string,
                "case": {
                    "id": job1.case.id,
                    "label": job1.case.label,
                    "description": job1.case.description,
                    "uri": job1.case.uri,
                    "thumbnail": job1.case.thumbnail
                }
            }, {
                "id": job2.id,
                "uri": job2.uri,
                "status": job2.status,
                "name": job2.name,
                "description": job2.description,
                "creation_datetime": nj.j2c_iso_string,
                "start_datetime": nj.j2s_iso_string,
                "end_datetime": nj.j2e_iso_string,
                "case": {
                    "id": job2.case.id,
                    "label": job2.case.label,
                    "description": job2.case.description,
                    "uri": job2.case.uri,
                    "thumbnail": job2.case.thumbnail
                }
            }, {
                "id": job3.id,
                "uri": job3.uri,
                "status": job3.status,
                "name": job3.name,
                "description": job3.description,
                "creation_datetime": nj.j3c_iso_string,
                "start_datetime": nj.j3s_iso_string,
                "end_datetime": nj.j3e_iso_string,
                "case": {
                    "id": job3.case.id,
                    "label": job3.case.label,
                    "description": job3.case.description,
                    "uri": job3.case.uri,
                    "thumbnail": job3.case.thumbnail
                }
            }
         ]}

        job_response = client.get(URI_STEMS['jobs'])
        assert job_response.status_code == 200
        # Both lists of dictionaries need to have same sort order to
        # successfully compare
        assert response_to_json(job_response)["jobs"]\
            .sort(key=lambda x: x["id"]) ==\
            expected_response["jobs"].sort(key=lambda x: x["id"])

    # === POST tests (CREATE) ===
    def test_post_for_nonexistent_job_returns_job_with_200(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        # Create job
        job = new_job1()
        job_response = client.post(URI_STEMS['jobs'],
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        # ignore differences in `creation_datetime` and `status` as these are
        # now modified directly by the api
        job_response_json = response_to_json(job_response)
        job.creation_datetime = \
            arrow.get(job_response_json['creation_datetime'])
        # middleware not currently responsible for status changes
        # job.status = 'new'
        job_json = job_to_json(job)

        assert job_response.status_code == 200
        assert job_response_json == job_json
        assert jobs.get_by_id(job.id) == job

    def test_post_for_existing_job_returns_error_with_409(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        # Create and store job
        job_existing = new_job1()
        jobs.create(job_existing)
        # Try and create a new job with the same ID
        job_new = new_job2()
        job_new.id = job_existing.id
        job_response = client.post(URI_STEMS['jobs'],
                                   data=json.dumps(job_to_json(job_new)),
                                   content_type='application/json')
        error_message = {"message": "Job with ID {} already "
                         "exists".format(job_existing.id)}
        assert job_response.status_code == 409
        assert response_to_json(job_response) == error_message
        assert jobs.get_by_id(job_existing.id) == job_existing

    def test_post_with_none_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job_response = client.post(URI_STEMS['jobs'], data=json.dumps(None),
                                   content_type='application/json')
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message
        assert len(jobs.list_ids()) == 0

    def test_post_with_nonjson_body_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        invalid_json = "{key-with-no-value}"
        # We don't add content_type='application/json' because, if we do the
        # framework catches invalid JSON before it gets to our response
        # handler
        job_response = client.post(URI_STEMS['jobs'], data=invalid_json)
        error_message = {"message":
                         "Message body could not be parsed as JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message
        assert len(jobs.list_ids()) == 0

    def test_post_with_invalid_job_json_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        invalid_job = {"no-id-field": "valid-json"}
        job_response = client.post(URI_STEMS['jobs'],
                                   data=json.dumps(invalid_job),
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
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'create_job_directory', side_effect=mock_create_job_directory)
    def test_run_with_valid_id(
            self,
            mock_tr,
            mock_patch,
            mock_run,
            mock_create_job_directory,
            session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id

        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("{}/{}".format(URI_STEMS['run'], job_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'j4s1source'
        assert job_response.status_code == 200

    def test_run_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2s3"

        job_response = client.post("{}/{}".format(URI_STEMS['run'], bad_id),
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
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id

        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("{}/{}".format(URI_STEMS['run'], job_id))

        err_message = {'message': ('Message body could not be parsed as JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400

    def test_run_with_invalid_json(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        broken_json = {'test': 5}

        job_response = client.post("{}/{}".format(URI_STEMS['run'], job_id),
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
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                'create_job_directory', side_effect=mock_create_job_directory)
    def test_setup_with_valid_id(
            self,
            mock_tr,
            mock_patch,
            mock_run,
            mock_create_job_directory,
            session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("{}/{}".format(URI_STEMS['setup'], job_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'j4s4source'
        assert job_response.status_code == 200

    def test_setup_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)
        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2sq3fdjkdfk"

        job_response = client.post("{}/{}".format(URI_STEMS['setup'], bad_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/setup/{0}] but did you '
                                   'mean /api/setup/<string:job_id>'
                                   ' ?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404

    def test_setup_with_no_json(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id

        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("{}/{}".format(URI_STEMS['setup'], job_id))

        err_message = {'message': ('Message body could not be parsed as JSON')}
        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 400

    def test_setup_with_invalid_json(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id

        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        broken_json = {'test': 5}

        job_response = client.post("{}/{}".format(URI_STEMS['setup'], job_id),
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
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.post("{}/{}".format(URI_STEMS['cancel'], job_id),
                                   data=json.dumps(job_to_json(job)),
                                   content_type='application/json')

        assert response_to_json(job_response)['stdout'] == 'j4s3source'
        assert job_response.status_code == 200

    def test_cancel_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2s439"

        job_response = client.post("{}/{}".format(URI_STEMS['cancel'], bad_id),
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
                '_run_remote_script', side_effect=mock_run_remote_return_json)
    def test_progress_with_valid_id(self, mock_run, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        job_response = client.get("{}/{}".format(
            URI_STEMS['progress'],
            job_id))

        assert response_to_json(job_response)['stdout']['name'] == 'j4s2source'
        assert job_response.status_code == 200

    def test_progress_with_invalid_id(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        cases = CaseRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        job = new_job4()
        job_id = job.id
        client.post(URI_STEMS['jobs'], data=json.dumps(job_to_json(job)),
                    content_type='application/json')

        bad_id = "2os3"

        job_response = client.get("{}/{}".format(
            URI_STEMS['progress'],
            bad_id),
            data=json.dumps(job_to_json(job)),
            content_type='application/json')

        err_message = {'message': ('Job {0} not found. You have requested '
                                   'this URI [/api/progress/{0}] but did '
                                   'you mean /api/progress/'
                                   '<string:job_id> ?').format(bad_id)}

        assert response_to_json(job_response) == err_message
        assert job_response.status_code == 404


class TestCasesApi(object):

    def test_get_cases_valid_request(self, session):
        cases = CaseRepositorySqlAlchemy(session)
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        # add an example case
        case1 = new_case1()
        session.add(case1)
        session.commit()

        response = client.get(URI_STEMS['cases'])

        expected_json = {
            "cases": [{
                "label": "c1label",
                'id': case1.id,
                'description': 'c1description',
                'thumbnail': 'c1thumbnail',
                'uri': 'c1uri'}
                ]}

        assert response.status_code == 200
        assert response_to_json(response) == expected_json


class TestCaseApi(object):

    def test_get_case_valid_request(self, session):
        cases = CaseRepositorySqlAlchemy(session)
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        # add an example case
        case = new_case1()
        case_id = case.id
        session.add(case)
        session.commit()

        response = client.get("{}/{}".format(URI_STEMS['cases'], case_id))
        response_json = response_to_json(response)

        expected_json = new_job1_output_json()

        # for now, igore differences in ID, uri, user, status and datetimes
        # (these are set by the middleware model and require mocking to test
        # full equality of response and expected_response)
        expected_json["id"] = response_json.get("id")
        expected_json["uri"] = response_json.get("uri")
        expected_json["user"] = response_json.get("user")
        expected_json["backend_identifier"] = response_json.get("backend_identifier")
        expected_json["status"] = response_json.get("status")
        expected_json["creation_datetime"] = \
            response_json.get("creation_datetime")
        expected_json["start_datetime"] = response_json.get("start_datetime")
        expected_json["end_datetime"] = response_json.get("end_datetime")

        assert response.status_code == 200
        assert response_json == expected_json

    def test_get_case_valid_request_invalid_case_id(self, session):

        cases = CaseRepositorySqlAlchemy(session)
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(case_repository=cases, job_repository=jobs)

        # add an example case ()
        case = new_case1()
        case_id = case.id
        session.add(case)
        session.commit()

        case_id = 'invalid-case'
        response = client.get("{}/{}".format(URI_STEMS['cases'], case_id))
        assert response.status_code == 404

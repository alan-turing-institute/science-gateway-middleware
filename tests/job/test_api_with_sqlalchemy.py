import json
import pytest
from flask import Flask
from werkzeug.exceptions import NotFound
from middleware.factory import create_app
from middleware.job.api import JobApi
from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.database import db as _db
from middleware.job.models import Job, Parameter, Template, Script, Input
from middleware.job.schema import job_to_json

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


def response_to_json(response):
    data = response.get_data(as_text=True)
    if not data:
        return None
    return json.loads(data)


def mock_api_post(job_id):
    return {"std out": [job_id], "std err": [job_id]}, 201


def new_job1():
    job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    job = Job(id=job_id)
    job.user = "j1user"
    job.parameters.append(Parameter(name="j1p1name", value="j1p1value"))
    job.parameters.append(Parameter(name="j1p2name", value="j1p2value"))
    job.templates.append(Template(source_uri="j1t1source",
                                  destination_path="j1t1_dest"))
    job.templates.append(Template(source_uri="j1t2source",
                                  destination_path="j1t2_dest"))
    job.scripts.append(Script(command="j1s1command", source_uri="j1s1source",
                              destination_path="j1s1_dest"))
    job.scripts.append(Script(command="j1s2command", source_uri="j1s2source",
                              destination_path="j212_dest"))
    job.inputs.append(Input(source_uri="j1i1source",
                            destination_path="j1i1_dest"))
    job.inputs.append(Input(source_uri="j1i2source",
                            destination_path="j1i2_dest"))
    return job


def new_job2():
    job_id = "9044394f-de29-4be3-857f-33a4fdca0be3"
    job = Job(id=job_id)
    job.user = "j2user"
    job.parameters.append(Parameter(name="j2p1name", value="j2p1value"))
    job.parameters.append(Parameter(name="j2p2name", value="j2p2value"))
    job.templates.append(Template(source_uri="j2t1source",
                                  destination_path="j2t1_dest"))
    job.templates.append(Template(source_uri="j2t2source",
                                  destination_path="j2t2_dest"))
    job.scripts.append(Script(command="j2s1command", source_uri="j2s1source",
                              destination_path="j2s1_dest"))
    job.scripts.append(Script(command="j2s2command", source_uri="j2s2source",
                              destination_path="j2s2_dest"))
    job.inputs.append(Input(source_uri="j2i1source",
                            destination_path="j2i1_dest"))
    job.inputs.append(Input(source_uri="j2i2source",
                            destination_path="j2i2_dest"))
    return job


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
        job_response = client.get("/job/{}".format(job1_id))

        assert job_response.status_code == 200
        assert response_to_json(job_response) == job1_json

    def test_get_for_nonexistent_job_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.get("/job/{}".format(job_id))
        error_message = {"message": "Job {} not found".format(job_id)}
        assert job_response.status_code == 404
        assert response_to_json(job_response) == error_message

    def test_get_with_no_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.get("/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    # === PUT tests (UPDATE) ===
    def test_put_with_no_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.put("/job/")
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
        job_response = client.put("/job/{}".format(job.id),
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
        job_response = client.put("/job/{}".format(job.id),
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
        job_response = client.put("/job/{}".format(job_id_url),
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
        job_response = client.put("/job/{}".format(job_id))
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
        job_response = client.put("/job/{}".format(job_id_orig),
                                  data=json.dumps(job_to_json(job_new)),
                                  content_type='application/json')
        assert job_response.status_code == 200
        assert response_to_json(job_response) == job_to_json(job_new)
        assert jobs.get_by_id(job_id_orig) == job_new

    def test_put_with_invalid_job_json_returns_error_with_400(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        # Create job
        job_orig = new_job1()
        job_id_orig = job_orig.id
        jobs.create(job_orig)
        client = test_client(jobs)
        invalid_job = {"no-id-field": "valid-json"}
        job_response = client.put("/job/{}".format(job_id_orig),
                                  data=json.dumps(invalid_job),
                                  content_type='application/json')
        error_message = {"message": "Message body is not valid Job JSON"}
        assert job_response.status_code == 400
        assert response_to_json(job_response) == error_message

    # === DELETE tests (DELETE) ===
    def test_delete_with_no_job_id_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_response = client.delete("/job/")
        assert job_response.status_code == 404
        # No content check as we are expecting the standard 404 error message
        # TODO: Get the 404 response defined for the app and compare it here

    def test_delete_with_nonexistent_job_returns_error_with_404(self, session):
        jobs = JobRepositorySqlAlchemy(session)
        client = test_client(jobs)
        job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
        job_response = client.delete("/job/{}".format(job_id))
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

        job_response = client.delete("/job/{}".format(job_id_orig))
        assert job_response.status_code == 204
        assert response_to_json(job_response) is None
        assert jobs.get_by_id(job_id_orig) is None

    # # === POST tests (patching) ===
    # @mock.patch('middleware.job.api.JobApi.post', side_effect=mock_api_post)
    # def test_patch_with_valid_json_and_correct_id(self, mock_post):
    #
    #     jobs = JobRepositoryMemory()
    #     client = test_client(jobs)
    #
    #     # Create skeleton job
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job = {"id": job_id, "parameters": {"height": 3}}
    #
    #     client.post("/job", data=json.dumps(job),
    #                 content_type='application/json')
    #
    #     # complete json with same id as before
    #     dest_path = 'project/case/'
    #     template_src = "./middleware/resources/templates/Blue.nml"
    #     script_src = "./middleware/resources/scripts/start_job.sh"
    #
    #     job_final = {"id": job_id,
    #                  "templates": [{"source_uri": template_src,
    #                                 "destination_path": dest_path}],
    #                  "scripts": [{"source_uri": script_src,
    #                               "destination_path": dest_path}],
    #                  "parameters": {"viscosity_properties":
    #                                 {"viscosity_phase_1": 0.09}},
    #                  "inputs": []}
    #
    #     job_response = client.post("/job/{}".format(job_id),
    #                                data=json.dumps(job_final),
    #                                content_type='application/json')
    #
    #     result = {"std out": [job_id], "std err": [job_id]}
    #
    #     assert response_to_json(job_response) == result
    #     assert job_response.status_code == 201
    #
    # # === PATCH tests (Partial UPDATE) ===
    # def test_patch_with_no_job_id_returns_error_with_404_status(self):
    #     jobs = JobRepositoryMemory()
    #     client = test_client(jobs)
    #     job_response = client.patch("/job/")
    #     assert job_response.status_code == 404
    #     # No content check as we are expecting the standard 404 error message
    #     # TODO: Get the 404 response defined for the app and compare it here
    #     assert len(jobs._jobs) == 0
    #
    # def test_patch_with_empty_body_returns_error_with_400_status(self):
    #     jobs = JobRepositoryMemory()
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job = {"id": job_id, "parameters": {"height": 3,
    #            "width": 4, "depth": 5}}
    #     jobs.create(job)
    #     job = None
    #     client = test_client(jobs)
    #     job_response = client.patch("/job/{}".format(job_id),
    #                                 data=json.dumps(job),
    #                                 content_type='application/json-patch+json')
    #     error_message = {"message": \
    #         "Message body could not be parsed as JSON"}
    #     assert job_response.status_code == 400
    #     assert response_to_json(job_response) == error_message
    #
    # def test_patch_with_nonjson_body_returns_error_with_400_status(self):
    #     jobs = JobRepositoryMemory()
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job = {"id": job_id, "parameters": {"height": 3,
    #            "width": 4, "depth": 5}}
    #     jobs.create(job)
    #     invalid_json = "{key-with-no-value}"
    #     client = test_client(jobs)
    #     # We don't add content_type='application/json' because, if we do the
    #     # framework catches invalid JSON before it gets to our response
    #     # handler
    #     job_response = client.patch("/job/{}".format(job_id),
    #                                 data=invalid_json)
    #     error_message = {"message": \
    #         "Message body could not be parsed as JSON"}
    #     assert job_response.status_code == 400
    #     assert response_to_json(job_response) == error_message
    #
    # def test_patch_for_nonexistent_job_id_returns_error_with_404(self):
    #     jobs = JobRepositoryMemory()
    #     client = test_client(jobs)
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_response = client.patch("/job/{}".format(job_id))
    #     error_message = {"message": "Job {} not found".format(job_id)}
    #     assert job_response.status_code == 404
    #     assert response_to_json(job_response) == error_message
    #
    # def test_patch_with_mismatched_job_id_returns_error_with_409(self):
    #     jobs = JobRepositoryMemory()
    #     # Create job
    #     job_id_url = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_existing = {"id": job_id_url, "parameters": {"height": 3,
    #                     "width": 4, "depth": 5}}
    #     jobs.create(job_existing)
    #     job_id_json = "59540b31-0454-4875-a00f-94eb4d81a09c"
    #     job_new = {"id": job_id_json, "parameters": {"height":
    #                7, "green": "low", "depth": None}}
    #     client = test_client(jobs)
    #     job_response = client.patch(
    #                     "/job/{}".format(job_id_url),
    #                     data=json.dumps(job_new),
    #                     content_type='application/merge-patch+json')
    #     error_message = {"message": "Job ID in URL ({}) does not match job "
    #                      "ID in message JSON ({}).".format(job_id_url,
    #                                                        job_id_json)}
    #     assert job_response.status_code == 409
    #     assert response_to_json(job_response) == error_message
    #     assert jobs.get_by_id(job_id_url) == job_existing
    #     assert jobs.get_by_id(job_id_json) is None
    #
    # def test_patch_with_existing_job_id_returns_new_job_with_200(self):
    #     jobs = JobRepositoryMemory()
    #     # Create job
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_original = {"id": job_id, "parameters": {"height": 3,
    #                     "width": 4, "depth": 5}}
    #     jobs.create(job_original)
    #     job_patch = {"parameters": {"height":
    #                  7, "green": "low", "depth": None}}
    #     job_new_expected = {"id": job_id, "parameters": {"height": 7,
    #                         "width": 4, "green": "low"}}
    #     client = test_client(jobs)
    #     job_response = client.patch(
    #                     "/job/{}".format(job_id),
    #                     data=json.dumps(job_patch),
    #                     content_type='application/merge-patch+json')
    #     assert job_response.status_code == 200
    #     assert response_to_json(job_response) == job_new_expected
    #     assert jobs.get_by_id(job_id) == job_new_expected


# class TestJobsApi(object):
#
#     # === GET tests (LIST) ===
#     def test_get_returns_object_summary_list(self):
#         jobs = JobRepositoryMemory()
#         # Create job
#         job_id_1 = "d769843b-6f37-4939-96c7-c382c3e74b46"
#         job_1 = {"id": job_id_1, "parameters": {"height": 11, "width": 12,
#                  "depth": 13}}
#         job_id_2 = "53835db6-87cb-4dd8-a91f-5c98100c0b82"
#         job_2 = {"id": job_id_2, "parameters": {"height": 21, "width": 22,
#                  "depth": 23}}
#         job_id_3 = "781692cc-b71c-469e-a8e9-938c2fda89f2"
#         job_3 = {"id": job_id_3, "parameters": {"height": 31, "width": 32,
#                  "depth": 33}}
#         jobs.create(job_1)
#         jobs.create(job_2)
#         jobs.create(job_3)
#         client = test_client(jobs)
#
#         def job_uri(job_id):
#             return "/job/{}".format(job_id)
#
#         expected_response = [{"id": job_id_1, "uri": job_uri(job_id_1)},
#                              {"id": job_id_2, "uri": job_uri(job_id_2)},
#                              {"id": job_id_3, "uri": job_uri(job_id_3)}]
#         job_response = client.get("/job")
#         assert job_response.status_code == 200
#         # Both lists of dictionaries need to have same sort order to
#         # successfully compare
#         assert response_to_json(job_response).sort(key=lambda x: x["id"]) ==\
#             expected_response.sort(key=lambda x: x["id"])
#
#     # === POST tests (CREATE) ===
#     def test_post_for_nonexistent_job_returns_job_with_200_status(self):
#         jobs = JobRepositoryMemory()
#         # Create job
#         job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
#         job = {"id": job_id,
#                "parameters": {"height": 3, "width": 4, "depth": 5}}
#         client = test_client(jobs)
#         job_response = client.post("/job", data=json.dumps(job),
#                                    content_type='application/json')
#         assert job_response.status_code == 200
#         assert response_to_json(job_response) == job
#         assert jobs.get_by_id(job_id) == job
#
#     def test_post_for_existing_job_returns_error_with_409_status(self):
#         jobs = JobRepositoryMemory()
#         # Create job
#         job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
#         job_existing = {"id": job_id, "parameters": {"height": 3, "width": 4,
#                         "depth": 5}}
#         jobs.create(job_existing)
#         job_new = {"id": job_id, "parameters": {"blue": "high",
#                    "green": "low"}}
#         client = test_client(jobs)
#         job_response = client.post("/job", data=json.dumps(job_new),
#                                    content_type='application/json')
#         error_message = {"message": "Job with ID {} already "
#                          "exists".format(job_id)}
#         assert job_response.status_code == 409
#         assert response_to_json(job_response) == error_message
#         assert jobs.get_by_id(job_id) == job_existing
#
#     def test_post_with_none_returns_error_with_400_status(self):
#         jobs = JobRepositoryMemory()
#         client = test_client(jobs)
#         job_response = client.post("/job", data=json.dumps(None),
#                                    content_type='application/json')
#         error_message = {"message": \
#             "Message body could not be parsed as JSON"}
#         assert job_response.status_code == 400
#         assert response_to_json(job_response) == error_message
#         assert len(jobs._jobs) == 0
#
#     def test_post_with_nonjson_body_returns_error_with_400_status(self):
#         jobs = JobRepositoryMemory()
#         invalid_json = "{key-with-no-value}"
#         client = test_client(jobs)
#         # We don't add content_type='application/json' because, if we do the
#         # framework catches invalid JSON before it gets to our response
#         # handler
#         job_response = client.post("/job", data=invalid_json)
#         error_message = {"message": \
#              "Message body could not be parsed as JSON"}
#         assert job_response.status_code == 400
#         assert response_to_json(job_response) == error_message
#
#     def test_post_with_invalid_job_json_returns_error_with_400_status(self):
#         jobs = JobRepositoryMemory()
#         invalid_job = {"no-id-field": "valid-json"}
#         client = test_client(jobs)
#         job_response = client.post("/job", data=json.dumps(invalid_job),
#                                    content_type='application/json')
#         error_message = {"message": "Message body is not valid Job JSON"}
#         assert job_response.status_code == 400
#         assert response_to_json(job_response) == error_message

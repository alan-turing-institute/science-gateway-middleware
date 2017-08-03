import pytest
from flask import Flask
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.factory import create_app
from middleware.database import db as _db
from middleware.job.models import Job, Parameter

TEST_DB_URI = 'sqlite://'

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
    """Session-wide test database session"""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


def job1():
    job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    job = Job(id=job_id)
    job.parameters.append(Parameter(name="j1p1", value="j1v1"))
    job.parameters.append(Parameter(name="j1p2", value="j1v2"))
    return job


def job2():
    job_id = "9044394f-de29-4be3-857f-33a4fdca0be3"
    job = Job(id=job_id)
    job.parameters.append(Parameter(name="j2p1", value="j2v1"))
    job.parameters.append(Parameter(name="j2p2", value="j2v2"))
    return job


class TestJobModels(object):

    def test_job_is_fully_stored_in_orm(self, session):
        # Store new Job
        job_orig = job1()
        session.add(job_orig)
        session.commit()
        # Try to read the same job back from the database
        jobs_db = session.query(Job).filter_by(id=job_orig.id)
        # Should only retrieve one job for a given ID
        assert jobs_db.count() == 1
        # Jobs should have identical fields
        job_db = jobs_db.first()
        # Test all fields at once to ensure we are not comparing references
        assert job_db.id == job_orig.id
        assert job_db.parameters[0].name == job_orig.parameters[0].name
        assert job_db.parameters[0].value == job_orig.parameters[0].value
        assert job_db.parameters[1].name == job_orig.parameters[1].name
        assert job_db.parameters[1].value == job_orig.parameters[1].value
        # NOTE: These are actually the same object
        assert id(job_db) == id(job_orig)


class TestJobRepositorySQLAlchemy(object):
    # Notes: We use dictionary.get(key) rather than dictionary[key] to ensure
    # we get None rather than KeyError if the key does not exist

    def test_new_repo_has_no_jobs(self, session):
        JobRepositorySqlAlchemy(session)
        # Count number of jobs in database
        num_jobs = session.query(Job.id).count()
        assert num_jobs == 0

    def test_exists_for_existing_job_returns_true(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = job1()
        session.add(job_orig)
        session.commit()
        # Check repo thinks job exists
        job_exists = repo.exists(job_orig.id)
        assert job_exists is True

    def test_exists_for_nonexistent_job_returns_false(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = job1()
        session.add(job_orig)
        session.commit()
        fetch_id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_returned = repo.exists(fetch_id)
        assert job_returned is False

    def test_exists_for_none_returns_false(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = job1()
        session.add(job_orig)
        session.commit()
        job_returned = repo.exists(None)
        assert job_returned is False

    def test_get_existing_job_by_id_returns_job(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = job1()
        session.add(job_orig)
        session.commit()
        job_returned = repo.get_by_id(job_orig.id)
        assert job_returned == job_orig

    def test_get_nonexistent_job_by_id_returns_none(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = job1()
        session.add(job_orig)
        session.commit()
        fetch_id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_returned = repo.get_by_id(fetch_id)
        assert job_returned is None

    # def test_create_nonexistent_job_creates_job(self):
    #     repo = JobRepositorySqlAlchemy()
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job = {"id": job_id,
    #            "parameters": {"height": 3, "width": 4, "depth": 5}}
    #     job_returned = repo.create(job)
    #     job_stored = repo._jobs.get(job_id)
    #     assert job_returned == job
    #     assert job_stored == job
    #
    # def test_create_existing_job_returns_none(self):
    #     repo = JobRepositorySqlAlchemy()
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_initial = {"id": job_id, "parameters": {"height": 3, "width": 4,
    #                    "depth": 5}}
    #     job_updated = {"id": job_id, "purple": {"circle": "street",
    #                    "triangle": "road", "square": "avenue"}}
    #     repo._jobs[job_id] = job_initial
    #     job_returned = repo.create(job_updated)
    #     job_stored = repo._jobs.get(job_id)
    #     assert job_returned is None
    #     assert job_stored is job_initial
    #
    # def test_update_replaces_existing_job_completely(self):
    #     repo = JobRepositorySqlAlchemy()
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_initial = {"id": job_id, "parameters": {"height": 3, "width": 4,
    #                    "depth": 5}}
    #     job_updated = {"id": job_id, "purple": {"circle": "street",
    #                    "triangle": "road", "square": "avenue"}}
    #     repo._jobs[job_id] = job_initial
    #     job_returned = repo.update(job_updated)
    #     job_stored = repo._jobs.get(job_id)
    #     assert job_returned == job_updated
    #     assert job_stored == job_updated
    #
    # def test_update_nonexistent_job_returns_none(self):
    #     repo = JobRepositorySqlAlchemy()
    #     job_id_initial = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_initial = {"id": job_id_initial, "parameters": {"height": 3,
    #                    "width": 4, "depth": 5}}
    #     job_id_updated = "ad460823-370c-48dd-a09f-a7564bb458f1"
    #     job_updated = {"id": job_id_updated, "purple": {"circle": "street",
    #                    "triangle": "road", "square": "avenue"}}
    #     repo._jobs[job_id_initial] = job_initial
    #     job_returned = repo.update(job_updated)
    #     job_stored_updated = repo._jobs.get(job_id_updated)
    #     job_stored_initial = repo._jobs.get(job_id_initial)
    #     assert job_returned is None
    #     assert job_stored_updated is None
    #     assert job_stored_initial == job_initial
    #
    # def test_delete_existing_job_deletes_job(self):
    #     repo = JobRepositorySqlAlchemy()
    #     job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job = {"id": job_id,
    #            "parameters": {"height": 3, "width": 4, "depth": 5}}
    #     repo._jobs[job_id] = job
    #     job_returned = repo.delete(job_id)
    #     job_stored = repo._jobs.get(job_id)
    #     assert job_returned is None
    #     assert job_stored is None
    #
    # def test_delete_nonexistent_job_returns_none(self):
    #     repo = JobRepositorySqlAlchemy()
    #     job_id_initial = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_initial = {"id": job_id_initial, "parameters": {"height": 3,
    #                    "width": 4, "depth": 5}}
    #     job_id_updated = "ad460823-370c-48dd-a09f-a7564bb458f1"
    #     repo._jobs[job_id_initial] = job_initial
    #     job_returned = repo.delete(job_id_updated)
    #     job_stored = repo._jobs.get(job_id_initial)
    #     assert job_returned is None
    #     assert job_stored == job_initial
    #
    # def test_list_ids_returns_all_ids(self):
    #     repo = JobRepositorySqlAlchemy()
    #     # Add multiple jobs to repo
    #     job_id_1 = "d769843b-6f37-4939-96c7-c382c3e74b46"
    #     job_1 = {"id": job_id_1, "parameters": {"height": 11, "width": 12,
    #              "depth": 13}}
    #     job_id_2 = "53835db6-87cb-4dd8-a91f-5c98100c0b82"
    #     job_2 = {"id": job_id_2, "parameters": {"height": 21, "width": 22,
    #              "depth": 23}}
    #     job_id_3 = "781692cc-b71c-469e-a8e9-938c2fda89f2"
    #     job_3 = {"id": job_id_3, "parameters": {"height": 31, "width": 32,
    #              "depth": 33}}
    #     repo._jobs[job_id_1] = job_1
    #     repo._jobs[job_id_2] = job_2
    #     repo._jobs[job_id_3] = job_3
    #     list_expected = [key for key, val in repo._jobs.items()]
    #     list_returned = repo.list_ids()
    #     assert list_returned == list_expected

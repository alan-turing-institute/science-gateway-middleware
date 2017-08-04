import pytest
from flask import Flask
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.database import db as _db
from middleware.job.models import Job, Parameter, Template, Script, Input

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


class TestJobModels(object):

    def test_single_job_is_fully_stored_in_orm(self, session):
        # Store new Job
        job_orig = new_job1()
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

    def test_multiple_jobs_are_fully_stored_in_orm(self, session):
        # Store new Jobs
        job1_orig = new_job1()
        job2_orig = new_job2()
        session.add(job1_orig)
        session.add(job2_orig)
        session.commit()
        # Try to read the same jobs back from the database
        jobs1_db = session.query(Job).filter_by(id=job1_orig.id)
        jobs2_db = session.query(Job).filter_by(id=job2_orig.id)
        # Should only retrieve one job for a given ID
        assert jobs1_db.count() == 1
        assert jobs2_db.count() == 1
        # Jobs should have identical fields
        job1_db = jobs1_db.first()
        job2_db = jobs2_db.first()
        # Test retrieved jobs are the same as their originals and different to
        # each other
        assert job1_db == job1_orig
        assert job2_db == job2_orig

    def test_fully_identical_jobs_evaluate_as_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        assert job1 == job2

    def test_full_jobs_differing_only_by_id_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        assert job1 != job2

    def test_full_jobs_differing_only_by_user_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.user = ""
        assert job1 != job2

    def test_full_jobs_differing_only_by_param_name_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.parameters[0].name = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_param_value_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.parameters[0].value = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_param_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.parameters[0]
        job2.parameters[0] = job2.parameters[1]
        job2.parameters[1] = temp
        assert job2.parameters[1] == job1.parameters[0]
        assert job2.parameters[0] == job1.parameters[1]
        assert job1 == job2

    def test_full_jobs_differing_only_by_template_source_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.templates[0].source_uri = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_template_dest_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.templates[0].destination_path = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_template_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.templates[0]
        job2.templates[0] = job2.templates[1]
        job2.templates[1] = temp
        assert job2.templates[1] == job1.templates[0]
        assert job2.templates[0] == job1.templates[1]
        assert job1 == job2

    def test_full_jobs_differing_only_by_script_command_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.scripts[0].command = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_script_source_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.scripts[0].source_uri = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_script_dest_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.scripts[0].destination_path = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_script_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.scripts[0]
        job2.scripts[0] = job2.scripts[1]
        job2.scripts[1] = temp
        assert job2.scripts[1] == job1.scripts[0]
        assert job2.scripts[0] == job1.scripts[1]
        assert job1 == job2

    def test_full_jobs_differing_only_by_input_source_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.inputs[0].source_uri = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_input_dest_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.inputs[0].destination_path = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_input_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.inputs[0]
        job2.inputs[0] = job2.inputs[1]
        job2.inputs[1] = temp
        assert job2.inputs[1] == job1.inputs[0]
        assert job2.inputs[0] == job1.inputs[1]
        assert job1 == job2


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
        job_orig = new_job1()
        session.add(job_orig)
        session.commit()
        # Check repo thinks job exists
        job_exists = repo.exists(job_orig.id)
        assert job_exists is True

    def test_exists_for_nonexistent_job_returns_false(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = new_job1()
        session.add(job_orig)
        session.commit()
        fetch_id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_returned = repo.exists(fetch_id)
        assert job_returned is False

    def test_exists_for_none_returns_false(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = new_job1()
        session.add(job_orig)
        session.commit()
        job_returned = repo.exists(None)
        assert job_returned is False

    def test_get_existing_job_by_id_returns_job(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = new_job1()
        session.add(job_orig)
        session.commit()
        job_returned = repo.get_by_id(job_orig.id)
        assert job_returned == job_orig

    def test_get_nonexistent_job_by_id_returns_none(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job independently of repo
        job_orig = new_job1()
        session.add(job_orig)
        session.commit()
        fetch_id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_returned = repo.get_by_id(fetch_id)
        assert job_returned is None

    def test_create_nonexistent_job_creates_job(self, session):
        repo = JobRepositorySqlAlchemy(session)
        job_orig = new_job1()
        # Store job using repo create()
        job_returned = repo.create(job_orig)
        # Try to read the same job back independent of the repo
        jobs_stored = session.query(Job).filter_by(id=job_orig.id)
        # Should only retrieve one job for a given ID
        assert jobs_stored.count() == 1
        # Jobs should have identical fields
        job_stored = jobs_stored.first()
        # We are relying on the Job objects retaining their reference (Python
        # ID) when they are stored via the ORM layer
        assert job_returned == job_orig
        assert job_stored == job_orig

    def test_create_job_with_existing_id_returns_none(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job in repo
        job_orig = new_job1()
        repo.create(job_orig)
        # Create identical job and update a single field
        job_updated = new_job1()
        job_updated.parameters[0].value = "new"
        # Try and create the updated object in the rep
        job_returned = repo.create(job_updated)
        job_stored = session.query(Job).filter_by(id=job_orig.id).first()
        assert job_returned is None
        assert job_stored is job_orig

    def test_update_replaces_existing_job_completely(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job in repo
        job_orig = new_job1()
        repo.create(job_orig)
        # Create identical job and update a single field
        job_updated = new_job1()
        job_updated.parameters[0].value = "new"
        # Try and update the original object with the copy
        job_returned = repo.update(job_updated)
        job_stored = session.query(Job).filter_by(id=job_orig.id).first()
        assert job_returned == job_updated
        assert job_stored == job_updated

    def test_update_nonexistent_job_returns_none(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job in repo
        job_orig = new_job1()
        repo.create(job_orig)
        # Create identical job and update a single field and also change ID
        job_updated = new_job1()
        job_updated.parameters[0].value = "new"
        job_updated.id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        # Try and update the original object with the copy
        job_returned = repo.update(job_updated)
        # Try and fetch job by original and updated IDs
        job_stored_updated = \
            session.query(Job).filter_by(id=job_updated.id).first()
        job_stored_orig = \
            session.query(Job).filter_by(id=job_orig.id).first()
        assert job_returned is None
        assert job_stored_updated is None
        assert job_stored_orig == job_orig

    def test_delete_existing_job_deletes_job(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job in repo
        job_orig = new_job1()
        repo.create(job_orig)
        job_returned = repo.delete(job_orig.id)
        job_stored = session.query(Job).filter_by(id=job_orig.id).first()
        assert job_returned is None
        assert job_stored is None

    def test_delete_nonexistent_job_returns_none(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store new Job in repo
        job_orig = new_job1()
        repo.create(job_orig)
        job_id_updated = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job_returned = repo.delete(job_id_updated)
        job_stored = session.query(Job).filter_by(id=job_orig.id).first()
        assert job_returned is None
        assert job_stored == job_orig

    def test_list_ids_returns_all_ids(self, session):
        repo = JobRepositorySqlAlchemy(session)
        # Store multiple jobs in repo
        job1 = new_job1()
        job2 = new_job2()
        session.add(job1)
        session.add(job2)
        session.commit()
        list_expected = [job1.id, job2.id]
        list_returned = repo.list_ids()
        assert sorted(list_returned) == sorted(list_expected)

import os
import re
import posixpath
import unittest.mock as mock
import pytest
from middleware.job_information_manager import job_information_manager as JIM
from middleware.ssh import ssh
from tests.job.new_jobs import new_job5
from instance.config import *
from middleware.job.schema import Template
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from flask import Flask
from middleware.database import db as _db
from werkzeug.exceptions import ServiceUnavailable


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


def abstract_getting_secrets():
    # This block allows us to test against local secrets or the
    # defaults generated when running our CI tests.
    secrets = [
        'SSH_USR', 'SSH_HOSTNAME', 'SSH_PORT', 'SIM_ROOT', 'PRIVATE_KEY_PATH']
    if all(x in globals() for x in secrets):
        username = SSH_USR
        hostname = SSH_HOSTNAME
        port = SSH_PORT
        simulation_root = SIM_ROOT
        private_key_path = PRIVATE_KEY_PATH
    else:
        username = 'test_user'
        hostname = 'test_host'
        port = 22
        simulation_root = '/home/test_user'
        private_key_path = None

    return username, hostname, port, simulation_root, private_key_path


def mock_mkdir(path, exist_ok=True):
    return True


def mock_apply_patch(template_path, parameters, destination_path):
    return template_path, parameters, destination_path


def mock_secure_copy(full_file_path, destination_path):
    return full_file_path, destination_path


def mock_close():
    return True


def mock_run_remote(script_name, remote_path, debug=True):
    return script_name, 'err', '0'


def mock_pass_command(command):
    return command, 'err', '0'


def mock_ssh_exception():
    raise Exception()


class TestJIM(object):

    def test_constructor_no_simulation_root(self):

        username, hostname, port, simulation_root, private_key_path = \
            abstract_getting_secrets()

        # Create a manager
        job = new_job5()
        jim = JIM(job)

        assert jim.username == username
        assert jim.hostname == hostname
        assert jim.port == port
        assert jim.job_id == job.id
        assert jim.template_list == job.templates
        assert jim.families == job.families
        assert jim.script_list == job.scripts
        assert jim.inputs_list == job.inputs
        assert jim.simulation_root == simulation_root
        assert jim.private_key_path == private_key_path
        assert jim.patched_templates == []
        assert jim.user == job.user

    def test_apply_patch(self, tmpdir):
        job = new_job5()
        manager = JIM(job)

        # create dict objects for parameters and templates

        families = job.families
        parameters = families[0].parameters
        parameter = parameters[0]  # choose first parameter

        templates = job.templates
        template = templates[0]  # choose first template

        template_path = template.source_uri
        in_parameter_value = parameter.value

        template_filename = os.path.basename(template_path)
        destination_path = os.path.join(tmpdir.strpath, template_filename)

        manager._apply_patch(template_path, parameters, destination_path)

        # read patched file
        with open(destination_path, "r") as f:
            content = f.readlines()

        for line in content:
            patched = re.search(r"^\s+viscosity_phase_1\s+=\s+(\S+)\s+!", line)
            if patched:
                patched_value = patched.group(1)
                assert patched_value == in_parameter_value
                break

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_apply_patch', side_effect=mock_apply_patch)
    def test_patched_templates_construction(self, mock_patch):
        job = new_job5()
        manager = JIM(job)

        manager.patch_all_templates()

        dest = job.templates[0].destination_path
        src = os.path.join('tmp', dest,
                           os.path.basename(job.templates[0].source_uri))

        expected = [Template(source_uri=src, destination_path=dest)]
        assert manager.patched_templates == expected

    @mock.patch('os.makedirs', side_effect=mock_mkdir)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_apply_patch', side_effect=mock_apply_patch)
    def test_patch_templates_path_construction(self, mock_patch, mock_mkdirs):
        job = new_job5()
        manager = JIM(job)
        manager.patch_all_templates()

        calls = mock_patch.call_args[0]

        exp_filename = os.path.basename(job.templates[0].source_uri)
        exp_path_1 = job.templates[0].source_uri
        exp_path_2 = os.path.join('tmp',
                                  job.templates[0].destination_path,
                                  exp_filename)

        assert calls[0] == exp_path_1
        assert calls[2] == exp_path_2

    @mock.patch(
        'middleware.ssh.ssh.close_connection', side_effect=mock_close)
    @mock.patch(
        'middleware.ssh.ssh.secure_copy', side_effect=mock_secure_copy)
    @mock.patch(
        'middleware.ssh.ssh.pass_command', side_effect=mock_pass_command)
    def test_transfer_all_files(
            self, mock_close, mock_secure_copy, mock_pass_command):
        username, hostname, port, simulation_root, private_key_path = \
            abstract_getting_secrets()
        job = new_job5()
        manager = JIM(job)
        with mock.patch.object(ssh, '__init__',
                               lambda self, *args, **kwargs: None):
            manager.transfer_all_files()
            calls = mock_secure_copy.call_args[0]

        job_working_directory_name = "{}-{}".format(job.case.label, job.id)

        expected_path = posixpath.join(
            simulation_root,
            job_working_directory_name,
            job.scripts[0].destination_path)

        assert calls[1] == expected_path

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_trigger_action_script_valid_verbs(self, mock_run):
        # TODO test DATA and PROGRESS
        for verb in ['RUN', 'SETUP', 'CANCEL']:

            job = new_job5()
            manager = JIM(job)
            message, code = manager.trigger_action_script(verb)

            first_arg = mock_run.call_args[0][0]

            exp_message = {'stdout': '{}'.format(first_arg),
                           'stderr': 'err', 'exit_code': '0'}

            assert code == 200
            assert message == exp_message

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_trigger_action_script_invalid_verb(self, mock_run):
        job = new_job5()
        action = 'JUMP'
        manager = JIM(job)
        message, code = manager.trigger_action_script(action)

        exp_message = {'message': '{} script not found'.format(action)}

        assert code == 400
        assert message == exp_message

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_ssh_connection', side_effect=mock_ssh_exception)
    def test_failed_ssh_connection_gives_503_exception(self, mock_run):
        # At least some of the standard Exceptions raised when setting up
        # an SCP connection in Paramiko do not get magically converted to
        # HTTP error responses by Flask. These tests ensure that we get
        # a ServiceUnavailable (503) Exception that Flask will magically pass
        # on to the client.
        job = new_job5()
        manager = JIM(job)
        expected_message = "Unable to connect to backend compute resource"
        expected_exception = ServiceUnavailable(description=expected_message)
        # Check correct Flask exception raised when updating status
        try:
            manager.update_job_status()
        except Exception as e:
            assert e == expected_exception
        # Check correct Flask exception raised when executing actions
        for action in ['RUN', 'SETUP', 'CANCEL', 'PROGRESS', 'DATA']:
            try:
                manager.trigger_action_script('action')
            except Exception as e:
                assert e == expected_exception

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=(
                    lambda script, path: ('5305301.cx1b\n', 'err', '0')))
    def test_job_status_is_submit_for_valid_imperial_pbs_id(
            self, mock_run, session):
        # On successful submission, RUN should change status ot "Queued",
        # regardless of the previous job status
        for s in ["New", "Queued", "Running", "Complete", "Error"]:
            job = new_job5()
            job.status = s
            repo = JobRepositorySqlAlchemy(session)
            manager = JIM(job, repo)
            message, code = manager.trigger_action_script("RUN")

            exp_message = {'stdout': '5305301.cx1b\n',
                           'stderr': 'err', 'exit_code': '0'}

            assert code == 200
            assert message == exp_message
            assert job.status == "Queued"

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=(
                    lambda script, path: ('93.science-gateway-cluster\n',
                                          'err', '0')))
    def test_job_status_is_submit_for_valid_azure_torque_id(
            self, mock_run, session):
        # On successful submission, RUN should change status ot "Queued",
        # regardless of the previous job status
        for s in ["New", "Queued", "Running", "Complete", "Error"]:
            job = new_job5()
            job.status = s
            repo = JobRepositorySqlAlchemy(session)
            manager = JIM(job, repo)
            message, code = manager.trigger_action_script("RUN")

            exp_message = {'stdout': '93.science-gateway-cluster\n',
                           'stderr': 'err', 'exit_code': '0'}

            assert code == 200
            assert message == exp_message
            assert job.status == "Queued"

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=(
                    lambda script, path: ('invalid\n', 'err', '0')))
    def test_job_status_is_not_submit_for_invalid_id(
            self, mock_run, session):
        # As mocked backend job ID is invalid, status should remain unchanged
        for s in ["New", "Queued", "Running", "Complete", "Error"]:
            job = new_job5()
            job.status = s
            repo = JobRepositorySqlAlchemy(session)
            manager = JIM(job, repo)
            message, code = manager.trigger_action_script("RUN")

            exp_message = {'stdout': 'invalid\n',
                           'stderr': 'err', 'exit_code': '0'}

            assert code == 200
            assert message == exp_message
            assert job.status == s

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_qstat_status', side_effect=(lambda: 'Q'))
    def test_job_status_updates_for_qstat_status_of_q(self, mock_qstat):
        # We only check the qstat queue if the job has been submitted but has
        # not completed
        for s in ["Queued", "Running"]:
            job = new_job5()
            job.status = s
            print(job.status)
            manager = JIM(job)
            updated_status = manager.update_job_status()
            assert updated_status == 'Queued'
        # All other initial statuses should be unchanged
        for s in ["New", "Complete", "Error", "Gibberish"]:
            job = new_job5()
            job.status = s
            manager = JIM(job)
            updated_status = manager.update_job_status()
            assert updated_status == s

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_qstat_status', side_effect=(lambda: 'R'))
    def test_job_status_updates_for_qstat_status_of_r(self, mock_qstat):
        # We only check the qstat queue if the job has been submitted but has
        # not completed
        for s in ["Queued", "Running"]:
            job = new_job5()
            job.status = s
            print(job.status)
            manager = JIM(job)
            updated_status = manager.update_job_status()
            assert updated_status == 'Running'
        # All other initial statuses should be unchanged
        for s in ["New", "Complete", "Error", "Gibberish"]:
            job = new_job5()
            job.status = s
            manager = JIM(job)
            updated_status = manager.update_job_status()
            assert updated_status == s

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_qstat_status', side_effect=(lambda: 'C'))
    def test_job_status_updates_for_qstat_status_of_c(self, mock_qstat):
        # We only check the qstat queue if the job has been submitted but has
        # not completed
        for s in ["Queued", "Running"]:
            job = new_job5()
            job.status = s
            print(job.status)
            manager = JIM(job)
            updated_status = manager.update_job_status()
            assert updated_status == 'Complete'
        # All other initial statuses should be unchanged
        for s in ["New", "Complete", "Error", "Gibberish"]:
            job = new_job5()
            job.status = s
            manager = JIM(job)
            updated_status = manager.update_job_status()
            assert updated_status == s

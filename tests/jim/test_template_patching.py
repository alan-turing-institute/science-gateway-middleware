import os
import re
import unittest.mock as mock
from middleware.job_information_manager import job_information_manager as JIM
from middleware.ssh import ssh
from instance.config import *

job = {
    "id": "d769843b-6f37-4939-96c7-c382c3e74b46",
    "templates": [
        {
            "source_uri": "./resources/templates/Blue.nml",
            "destination_path": "project/case/"
        }
    ],
    "scripts": [
        {
            "source_uri": "./resources/scripts/start_job.sh",
            "destination_path": "project/case/"
        }
    ],
    "parameters": {
        "viscosity_properties": {
            "viscosity_phase_1": "42.0"
        }
    },
    "inputs": []
}

job2 = {
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


def abstract_getting_secrets():
    # This block allows us to test against local secrets or the
    # defaults generated when running our CI tests.
    secrets = ['SSH_USR', 'SSH_HOSTNAME', 'SSH_PORT', 'SIM_ROOT']
    if all(x in globals() for x in secrets):
        username = SSH_USR
        hostname = SSH_HOSTNAME
        port = SSH_PORT
        simulation_root = SIM_ROOT
    else:
        username = 'test_user'
        hostname = 'test_host'
        port = 22
        simulation_root = '/home/'

    return username, hostname, port, simulation_root


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


class TestJIM(object):

    def test_constructor_no_simulation_root(self):

        username, hostname, port, simulation_root = abstract_getting_secrets()

        # Create a manager
        jim = JIM(job)

        assert jim.username == username
        assert jim.hostname == hostname
        assert jim.port == port
        assert jim.job_id == job['id']
        assert jim.template_list == job['templates']
        assert jim.parameter_patch == job['parameters']
        assert jim.script_list == job['scripts']
        assert jim.inputs_list == job['inputs']
        assert jim.simulation_root == simulation_root
        assert jim.patched_templates == []

    def test_constructor_with_simulation_root(self):

        username, hostname, port, simulation_root = abstract_getting_secrets()

        # Create a manager
        jim = JIM(job2)

        assert jim.username == username
        assert jim.hostname == hostname
        assert jim.port == port
        assert jim.job_id == job2['id']
        assert jim.template_list == job2['templates']
        assert jim.parameter_patch == job2['parameters']
        assert jim.script_list == job2['scripts']
        assert jim.inputs_list == job2['inputs']
        assert jim.simulation_root == simulation_root
        assert jim.patched_templates == []

    def test_apply_patch(self, tmpdir):
        manager = JIM(job)

        template_path = job["templates"][0]["source_uri"]
        template_filename = os.path.basename(template_path)
        parameters = job["parameters"]
        destination_path = os.path.join(tmpdir.strpath, template_filename)

        manager._apply_patch(template_path, parameters, destination_path)

        # eg the string "42.0"
        in_val = job["parameters"]["viscosity_properties"]["viscosity_phase_1"]

        # read patched file
        with open(destination_path, "r") as f:
            content = f.readlines()

        for line in content:
            patched = re.search(r"^\s+viscosity_phase_1\s+=\s+(\S+)\s+!", line)
            if patched:
                patched_value = patched.group(1)
                assert patched_value == in_val
                break

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_apply_patch', side_effect=mock_apply_patch)
    def test_patched_templates_construction(self, mock_patch):
        manager = JIM(job)

        manager.patch_all_templates()

        dest = job['templates'][0]['destination_path']
        src = os.path.join('tmp', dest,
                           os.path.basename(job['templates'][0]['source_uri']))

        expected = [{'source_uri': src, 'destination_path': dest}]
        assert manager.patched_templates == expected

    @mock.patch('os.makedirs', side_effect=mock_mkdir)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_apply_patch', side_effect=mock_apply_patch)
    def test_patch_templates_path_construction(self, mock_patch, mock_mkdirs):
        manager = JIM(job)
        manager.patch_all_templates()

        calls = mock_patch.call_args[0]

        exp_filename = os.path.basename(job['templates'][0]['source_uri'])
        exp_path_1 = job['templates'][0]['source_uri']
        exp_path_2 = os.path.join('tmp',
                                  job['templates'][0]['destination_path'],
                                  exp_filename)

        assert calls[0] == exp_path_1
        assert calls[2] == exp_path_2

    @mock.patch('middleware.ssh.ssh.close_connection', side_effect=mock_close)
    @mock.patch('middleware.ssh.ssh.secure_copy', side_effect=mock_secure_copy)
    def test_transfer_all_files(self, mock_copy, mock_close):
        username, hostname, port, simulation_root = abstract_getting_secrets()
        manager = JIM(job2)
        with mock.patch.object(ssh, '__init__',
                               lambda self, *args, **kwargs: None):
            manager.transfer_all_files()
            calls = mock_copy.call_args[0]

        exp_path = os.path.join(simulation_root,
                                job2['scripts'][0]['destination_path'])

        assert calls[1] == exp_path

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_run_action_script_valid_verbs(self, mock_run):
        # Test that the 4 verbs work
        for verb in ['RUN', 'SETUP', 'CANCEL', 'PROGRESS']:

            manager = JIM(job2)
            message, code = manager.run_action_script(verb)

            first_arg = mock_run.call_args[0][0]

            exp_message = {'stdout': '{}'.format(first_arg),
                           'stderr': 'err', 'exit_code': '0'}

            assert code == 200
            assert message == exp_message

    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_run_remote_script', side_effect=mock_run_remote)
    def test_run_action_script_invalid_verb(self, mock_run):
        action = 'JUMP'
        manager = JIM(job2)
        message, code = manager.run_action_script(action)

        exp_message = {'message': '{} script not found'.format(action)}

        assert code == 400
        assert message == exp_message

import pytest
import os
import re
import unittest.mock as mock
from middleware.job_information_manager import job_information_manager as JIM
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
    "inputs": [{"simulation_root": "/home/"}]
}


def abstract_getting_secrets():
    # This block allows us to test against local secrets or the
    # defaults generated when running our CI tests.
    secrets = ['SSH_USR', 'SSH_HOSTNAME', 'SSH_PORT']
    if all(x in globals() for x in secrets):
        username = SSH_USR
        hostname = SSH_HOSTNAME
        port = SSH_PORT
    else:
        username = 'test_user'
        hostname = 'test_host'
        port = 22

    return username, hostname, port


def mock_mkdir(path, exist_ok=True):
    return True


def mock_apply_patch(template_path, parameters, destination_path):
    return template_path, parameters, destination_path


class TestJIM(object):

    def test_constructor_no_simulation_root(self):

        username, hostname, port = abstract_getting_secrets()

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
        assert jim.simulation_root == ''

    def test_constructor_with_simulation_root(self):

        username, hostname, port = abstract_getting_secrets()

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
        assert jim.simulation_root == '/home/'

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

    @mock.patch('os.makedirs', side_effect=mock_mkdir)
    @mock.patch('middleware.job_information_manager.job_information_manager.'
                '_apply_patch', side_effect=mock_apply_patch)
    def test_bulk_patch_path_construction(self, mock_patch, mock_mkdirs):
        manager = JIM(job)
        manager.bulk_patch()

        calls = mock_patch.call_args[0]

        exp_filename = os.path.basename(job['templates'][0]['source_uri'])
        exp_path_1 = job['templates'][0]['source_uri']
        exp_path_2 = os.path.join('tmp/',
                                  job['templates'][0]['destination_path'],
                                  exp_filename)

        assert calls[0] == exp_path_1
        assert calls[2] == exp_path_2

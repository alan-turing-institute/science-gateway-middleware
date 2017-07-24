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

simulation_root = ""


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


def mock_run_remote_script(script_name, remote_path, debug=True):
    return 'out', 'err', 5


class TestJIM(object):

    def test_constructor(self):

        username, hostname, port = abstract_getting_secrets()

        # Create a manager
        jim = JIM(job, simulation_root)

        assert jim.username == username
        assert jim.hostname == hostname
        assert jim.port == port
        assert jim.simulation_root == simulation_root
        assert jim.job_id == job['id']
        assert jim.template_list == job['templates']
        assert jim.parameter_patch == job['parameters']
        assert jim.script_list == job['scripts']

    @mock.patch(('middleware.job_information_manager.job_information_manager.'
                 '_run_remote_script'), side_effect=mock_run_remote_script)
    def test_run_list_of_scripts(self, mock_run):

        username, hostname, port = abstract_getting_secrets()

        jim = JIM(job, simulation_root)
        stdout, stderr, errcode = jim.run_remote_scripts()

        assert stdout == ['out']
        assert stderr == ['err']
        assert errcode == [5]

    def test_apply_patch(self, tmpdir):
        manager = JIM(job, simulation_root=simulation_root)

        template_path = job["templates"][0]["source_uri"]
        template_filename = os.path.basename(template_path)
        parameters = job["parameters"]
        destination_path = os.path.join(tmpdir, template_filename)

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

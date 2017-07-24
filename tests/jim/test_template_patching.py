import pytest
from middleware.job_information_manager import job_information_manager as JIM
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

import os
import re

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

class TestJIM(object):

    def test_apply_patch(self, tmpdir):
        manager = JIM(job, simulation_root=simulation_root)

        template_path = job["templates"][0]["source_uri"]
        template_filename = os.path.basename(template_path)
        parameters = job["parameters"]
        destination_path = os.path.join(tmpdir, template_filename)

        manager._apply_patch(template_path, parameters, destination_path)

        # eg the string "42.0"
        intended_value = job["parameters"]["viscosity_properties"]["viscosity_phase_1"]

        # read patched file
        with open(destination_path, "r") as f:
            content = f.readlines()

        for line in content:
            patched = re.search(r"^\s+viscosity_phase_1\s+=\s+(\S+)\s+!", line)
            if patched:
                patched_value = patched.group(1)
                assert patched_value == intended_value
                break

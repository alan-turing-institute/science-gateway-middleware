import pytest
from middleware.job_information_manager import job_information_manager as JIM


class TestJIM(object):
    def test_constructor(self):

        # These variables should come from instance/config.py
        username = ''
        ssh_host = ''
        port = 22

        # Some testing data
        simulation_root = 'path/to/test'
        job = {'id': '1234', 'templates': 'test_template',
               'scripts': 'test_script', 'parameters': 'viscosity'}

        # Create a manager
        jim = JIM(job, simulation_root)

        assert jim.username == username
        assert jim.hostname == ssh_host
        assert jim.port == port
        assert jim.simulation_root == simulation_root
        assert jim.job_id == job['id']
        assert jim.template_list == job['templates']
        assert jim.parameter_patch == job['parameters']
        assert jim.script_list == job['scripts']

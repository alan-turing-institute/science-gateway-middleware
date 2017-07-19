from secrets import *
from mako.template import Template
from middleware.ssh import ssh
import os
from os.path import dirname
from os.path import basename
from os import makedirs


class job_information_manager():

    def __init__(self, request, simulation_root=''):

        # gathering the needed info from our secrets file
        self.username = SSH_USR
        self.hostname = SSH_HOSTNAME
        if SSH_PORT:
            self.port = SSH_PORT
        else:
            self.port = 22

        # TODO build data structure here with full remote path information, so
        # generating full paths is a once only operation
        self.job_id = request.json['id']
        self.template_list = request.json['templates']
        self.parameter_patch = request.json['parameters']
        self.script_list = request.json['scripts']

        self.simulation_root = simulation_root

    def _apply_patch(self, template_path, parameters, destination_path):
        template = Template(filename=template_path)
        with open(destination_path, "w") as f:
            f.write(template.render(parameters=parameters))

    def patch_and_transfer(self):
        connection = ssh(self.hostname, self.username, self.port, debug=True)

        for template in self.template_list:
            template_file = template["source_uri"]
            template_filename = basename(template_file)

            destination_path = os.path.join(self.simulation_root,
                                            template["destination_path"])

            tmp_path = os.path.join('tmp', template["destination_path"])
            tmp_file = os.path.join(tmp_path, template_filename)
            makedirs(tmp_path, exist_ok=True)

            self._apply_patch(template_file, self.parameter_patch, tmp_file)
            connection.secure_copy(tmp_file, destination_path)
        connection.close_connection()

    def transfer_scripts(self):
        connection = ssh(self.hostname, self.username, self.port, debug=True)

        for file_object in self.script_list:
            file_full_path = file_object["source_uri"]
            destination_path = os.path.join(self.simulation_root,
                                            file_object["destination_path"])
            connection.secure_copy(file_full_path, destination_path)
        connection.close_connection()

    def run_remote_script(self, script_name, remote_path, debug=True):
        connection = ssh(self.hostname, self.username, self.port, debug=True)
        command = "cd {}; bash {}".format(remote_path, script_name)
        out = connection.pass_command(command)
        if debug:
            print(out)

    def run_remote_scripts(self, debug=True):
        for script in self.script_list:
            remote_location = os.path.join(self.simulation_root,
                                           script["destination_path"])
            self.run_remote_script(script, remote_location, debug=debug)

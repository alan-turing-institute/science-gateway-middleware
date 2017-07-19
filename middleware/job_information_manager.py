import os
from mako.template import Template
from middleware.ssh import ssh
from secrets import *


class job_information_manager():
    '''
    Class to handle patching parameter files, and the transfer of these files
    to the cluster alongside the transfer and execution of scripts to the
    cluster.

    Needs a better, descriptive name.
    '''

    def __init__(self, request, simulation_root=''):
        '''
        Create a manager object, which is populated with ssh information from
        secrets.py and the job information passed via http post in the api.
        '''
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
        '''
        Method to apply a patch based on a supplied template file.
        Shouldnt be called directly, access via the patch_and_transfer method.
        '''
        template = Template(filename=template_path)
        with open(destination_path, "w") as f:
            f.write(template.render(parameters=parameters))

    def patch_and_transfer(self):
        '''
        Connect to the remote server, patch all of the parameter files provided
        and transfer them to the remote server.
        '''
        connection = ssh(self.hostname, self.username, self.port, debug=True)

        for template in self.template_list:
            template_file = template["source_uri"]
            template_filename = os.path.basename(template_file)

            destination_path = os.path.join(self.simulation_root,
                                            template["destination_path"])

            tmp_path = os.path.join('tmp', template["destination_path"])
            tmp_file = os.path.join(tmp_path, template_filename)
            os.makedirs(tmp_path, exist_ok=True)

            self._apply_patch(template_file, self.parameter_patch, tmp_file)
            connection.secure_copy(tmp_file, destination_path)
        connection.close_connection()

    def transfer_scripts(self):
        '''
        Method to copy multiple scripts to the cluster using single
        ssh connection.
        '''
        connection = ssh(self.hostname, self.username, self.port, debug=True)

        for file_object in self.script_list:
            file_full_path = file_object["source_uri"]
            destination_path = os.path.join(self.simulation_root,
                                            file_object["destination_path"])
            connection.secure_copy(file_full_path, destination_path)
        connection.close_connection()

    def _run_remote_script(self, script_name, remote_path, debug=True):
        '''
        Method to run a given script, located in a remote location.
        Set the debug flag to print stdout to the terminal, and to enable
        logging in ./logs/ssh.log
        Shouldnt be called directly, access via the run_remote_scripts method.
        '''
        connection = ssh(self.hostname, self.username, self.port, debug=True)
        command = "cd {}; bash {}".format(remote_path, script_name)
        out, err = connection.pass_command(command)
        if debug:
            print(out)
        return out, err

    def run_remote_scripts(self, debug=True):
        '''
        Wrapper around _run_remote_script to simplify the interface and allow
        mutiple scripts to be run sequentially on a remote server.
        Set the debug flag to print stdout to the terminal, and to enable
        logging in ./logs/ssh.log
        '''
        std_errs = []
        std_outs = []

        for script in self.script_list:
            remote_location = os.path.join(self.simulation_root,
                                           script["destination_path"])
            script_name = os.path.basename(script['source_uri'])
            out, err = self._run_remote_script(script_name, remote_location,
                                               debug=debug)
            std_outs.append(out)
            std_errs.append(err)
        return std_outs, std_errs

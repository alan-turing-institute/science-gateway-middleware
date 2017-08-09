import os
from mako.template import Template
from middleware.ssh import ssh
from instance.config import *


class job_information_manager():
    '''
    Class to handle patching parameter files, and the transfer of these files
    to the cluster alongside the transfer and execution of scripts to the
    cluster.

    Needs a better, descriptive name.
    '''

    def __init__(self, job):
        '''
        Create a manager object, which is populated with ssh information from
        instance/config.py and job information passed via http post in the api.
        '''
        # Gathering the needed info from our secrets file. If the info is not
        # there, populate the instance variables with dummy data.
        secrets = ['SSH_USR', 'SSH_HOSTNAME', 'SSH_PORT', 'SIM_ROOT']
        if all(x in globals() for x in secrets):
            self.username = SSH_USR
            self.hostname = SSH_HOSTNAME
            self.port = SSH_PORT
            self.simulation_root = SIM_ROOT
        else:
            self.username = 'test_user'
            self.hostname = 'test_host'
            self.port = 22
            self.simulation_root = '/home/'

        # TODO build data structure here with full remote path information, so
        # generating full paths is a once only operation
        self.job = job
        self.job_id = job.id
        self.template_list = job.templates
        self.patched_templates = []
        self.parameter_patch = job.parameters
        self.script_list = job.scripts
        self.inputs_list = job.inputs
        self.user = job.user

    def _apply_patch(self, template_path, parameters, destination_path):
        '''
        Method to apply a patch based on a supplied template file.
        Access via the patch_all_templates method.
        '''
        template = Template(filename=template_path)
        with open(destination_path, "w") as f:
            f.write(template.render(parameters=parameters))

    def patch_all_templates(self):
        '''
        Wrapper around the _apply_patch method which patches all files in
        self.template_list
        '''
        for template in self.template_list:
            template_file = template.source_uri
            template_filename = os.path.basename(template_file)

            tmp_path = os.path.join('tmp', template.destination_path)
            tmp_file = os.path.join(tmp_path, template_filename)
            os.makedirs(tmp_path, exist_ok=True)

            self._apply_patch(template_file, self.parameter_patch, tmp_file)
            # TODO: this will break with the new object model of jobs.
            patched_paths = {'source_uri': tmp_file,
                             'destination_path': template["destination_path"]}

            self.patched_templates.append(patched_paths)

    def transfer_all_files(self):
        '''
        Method to copy all needed files to the cluster using a single
        ssh connection.
        '''
        connection = ssh(self.hostname, self.username, self.port, debug=True)

        all_files = [self.script_list, self.patched_templates,
                     self.inputs_list]

        for file_list in all_files:
            for file_object in file_list:
                file_full_path = file_object.source_uri
                dest_path = os.path.join(self.simulation_root,
                                         file_object.destination_path)
                connection.secure_copy(file_full_path, dest_path)
        connection.close_connection()

    def _run_remote_script(self, script_name, remote_path, debug=True):
        '''
        Method to run a given script, located in a remote location.
        Set the debug flag to print stdout to the terminal, and to enable
        logging in ./logs/ssh.log
        Shouldnt be called directly.
        '''
        connection = ssh(self.hostname, self.username, self.port, debug=True)
        command = "cd {}; bash {}".format(remote_path, script_name)
        out, err, exit_code = connection.pass_command(command)
        if debug:
            print(out)
        return out, err, exit_code

    def run_action_script(self, action):
        '''
        Pass in the job and the required action (eg 'RUN' or 'CANCEL')
        and this method will run the remote script which
        corresponds to that action
        '''
        to_run = None

        # Cycle through the list of scripts to to get the action script
        for i, s in enumerate(self.script_list):
            if s.command == action:
                to_run = self.script_list[i]
                break

        # If the script isn't found, return a 400 error
        if to_run:
            script_name = os.path.basename(to_run.source_uri)
            script_path = os.path.join(self.simulation_root,
                                       to_run.destination_path)

            a, b, c = self._run_remote_script(script_name, script_path)
            result = {"stdout": a, "stderr": b, "exit_code": c}
            return result, 200
        else:
            result = {'message': '{} script not found'.format(action)}
            return result, 400

    def run(self):
        '''
        This is the RUN behaviour for this job manager. This method ignores
        any data passed as part of the request.
        '''
        # Call setup to ensure that the latest params and files are loaded
        self.setup()

        # Now execute the run script
        return self.run_action_script('RUN')

    def setup(self):
        '''
        This is the SETUP behaviour for this job manager. This method ignores
        any data passed as part of the request.
        '''
        # PATCH EVERYTHING
        self.patch_all_templates()

        # COPY EVERYTHING
        self.transfer_all_files()

        # EXECUTE SETUP SCRIPT
        return self.run_action_script('SETUP')

    def progress(self):
        '''
        This is the PROGRESS behaviour for this job manager. Method ignores
        any data passed as part of the request.
        TODO: Figure out how to track progress and add that code here!
        '''
        # Execute the progress script
        return self.run_action_script('PROGRESS')

    def cancel(self):
        '''
        This is the CANCEL behaviour for this job manager. Method ignores
        any data passed as part of the request.
        '''
        # Execute the cancel script
        return self.run_action_script('CANCEL')

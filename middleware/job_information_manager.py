import os
from pathlib import posixpath
from mako.template import Template as MakoTemplate
from middleware.job.schema import Template
from middleware.ssh import ssh
import re
from instance.config import *


class job_information_manager():
    """
    Class to handle patching parameter files, and the transfer of these files
    to the cluster alongside the transfer and execution of scripts to the
    cluster.

    Needs a better, descriptive name.
    """

    def __init__(self, job, job_repository=None):
        """
        Create a manager object, which is populated with ssh information from
        instance/config.py and job information passed via http post in the api.
        """
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
            self.simulation_root = '/home/test_user'

        self.job = job
        self.jobs = job_repository

        self.job_id = job.id
        self.template_list = job.templates
        self.patched_templates = []
        self.families = job.families
        self.script_list = job.scripts
        self.inputs_list = job.inputs
        self.user = job.user
        self.extracted_parameters = \
            self._extract_parameters(self.families)

        # TODO case_label cannot contain spaces
        # (test for this in CaseSchema.make_case())
        self.case_label = self.job.case.label
        self.job_working_directory_name = "{}-{}".format(self.case_label,
                                                         self.job_id)
        self.job_working_directory_path = posixpath.join(
            self.simulation_root,
            self.job_working_directory_name)

    def _extract_parameters(self, families):
        parameters = []
        for family in families:
            parameters.extend(family.parameters)

    def _parameters_to_mako_dict(self, parameters):
        mako_dict = {}
        if parameters:
            for p in parameters:
                mako_dict[p["name"]] = p["value"]
        return mako_dict

    def _apply_patch(self, template_path, parameters, destination_path):
        """
        Method to apply a patch based on a supplied template file.
        Access via the patch_all_templates method.
        """
        template = MakoTemplate(filename=template_path, input_encoding='utf-8')
        mako_dict = self._parameters_to_mako_dict(parameters)

        with open(destination_path, "w") as f:
            f.write(template.render(parameters=mako_dict))

    def patch_all_templates(self):
        """
        Wrapper around the _apply_patch method which patches all files in
        self.template_list
        """

        for template in self.template_list:

            template_file = template.source_uri
            template_filename = os.path.basename(template_file)

            # make a dedicated directory for patching
            # TODO make temporary directory for each new job-id
            if template.destination_path:
                tmp_path = os.path.join('tmp', template.destination_path)
            else:
                tmp_path = template.destination_path

            tmp_file = os.path.join(tmp_path, template_filename)
            os.makedirs(tmp_path, exist_ok=True)

            self._apply_patch(template_file,
                              self.extracted_parameters,
                              tmp_file)
            patched_tempate = Template(
                source_uri=tmp_file,
                destination_path=template.destination_path)

            self.patched_templates.append(patched_tempate)

    def create_job_directory(self, debug=False):
        """
        Create a job directory (All inputs, scripts, templates are transferred
        relative to this location). The job directory is named using the
        following path structure:
            SIM_ROOT/<case.label>-<job.id>
        """
        connection = ssh(self.hostname, self.username, self.port, debug=True)

        command = "mkdir -p {}".format(self.job_working_directory_path)
        out, err, exit_code = connection.pass_command(command)
        if debug:
            print(out)
        return out, err, exit_code

    def transfer_all_files(self):
        """
        Method to copy all needed files to the cluster using a single
        ssh connection.
        """
        connection = ssh(self.hostname, self.username, self.port, debug=True)

        all_files = []
        all_files.extend(self.script_list)
        all_files.extend(self.inputs_list)
        all_files.extend(self.patched_templates)

        # these are Script and Input model objects
        for file_object in all_files:
            file_full_path = file_object.source_uri
            if file_object.destination_path:
                dest_path = posixpath.join(
                    self.job_working_directory_path,
                    file_object.destination_path)
            else:  # support {"destination_path": null} in job json
                dest_path = self.job_working_directory_path
            connection.secure_copy(file_full_path, dest_path)

        connection.close_connection()

    def _run_remote_script(self, script_name, remote_path, debug=False):
        """
        Method to run a given script, located in a remote location.
        Set the debug flag to print stdout to the terminal, and to enable
        logging in ./logs/ssh.log
        Shouldnt be called directly.
        """
        connection = ssh(self.hostname, self.username, self.port, debug=True)
        command = "cd {}; bash {}".format(remote_path, script_name)
        out, err, exit_code = connection.pass_command(command)
        if debug:
            print(out)
        return out, err, exit_code

    def _check_for_backend_identifier(self, string):
        """
        Check for PBS backend_identifier:
        Valid examples:
            "5305301.cx1b\n"
        Invalid examples:
            "d305e01.cx1b\n"
            "5305301.cx2b\n"
        """

        stripped_string = string.strip("\n")
        if re.match(r"\d+\.cx1b", stripped_string):
            return stripped_string
        else:
            return None

    def trigger_action_script(self, action):
        """
        Pass in the job and the required action (eg 'RUN' or 'CANCEL')
        and this method will run the remote script which
        corresponds to that action
        """
        to_trigger = None

        # Cycle through the list of scripts to to get the action script
        for i, s in enumerate(self.script_list):
            if s.action == action:
                to_trigger = self.script_list[i]
                break

        # If the script isn't found, return a 400 error
        if to_trigger:
            script_name = os.path.basename(to_trigger.source_uri)
            if to_trigger.destination_path:
                script_path = posixpath.join(
                    self.job_working_directory_path,
                    to_trigger.destination_path)
            else:  # support {"destination_path": null} in job json
                script_path = self.job_working_directory_path

            out, err, exit = self._run_remote_script(script_name, script_path)

            # for "RUN" actions, we need to persist the backend identifier
            # and submission status to the database
            if to_trigger.action == "RUN":
                backend_identifier = self._check_for_backend_identifier(out)
                if backend_identifier:
                    self.job.backend_identifier = backend_identifier
                    self.job.status = "submitted"
                    self.jobs.update(self.job)

            result = {"stdout": out, "stderr": err, "exit_code": exit}
            return result, 200
        else:
            result = {'message': '{} script not found'.format(action)}
            return result, 400

    def run(self):
        """
        This is the RUN behaviour for this job manager. This method ignores
        any data passed as part of the request.
        """
        # Call setup to ensure that the latest params and files are loaded
        self.setup()

        # Now execute the run script
        return self.trigger_action_script('RUN')

    def setup(self):
        """
        This is the SETUP behaviour for this job manager. This method ignores
        any data passed as part of the request.
        """
        # PATCH EVERYTHING
        self.patch_all_templates()

        # CREATE REQUIRED REMOTE DIRECTORIES
        self.create_job_directory()

        # COPY EVERYTHING
        self.transfer_all_files()

        # EXECUTE SETUP SCRIPT
        return self.trigger_action_script('SETUP')

    def progress(self):
        """
        This is the PROGRESS behaviour for this job manager. Method ignores
        any data passed as part of the request.
        TODO: Figure out how to track progress and add that code here!
        """
        # Execute the progress script
        return self.trigger_action_script('PROGRESS')


    def data(self):
        """
        This is the DATA behaviour for this job manager. Method ignores
        any data passed as part of the request.
        TODO: Figure out how to track progress and add that code here!
        """
        # Execute the progress script
        return self.trigger_action_script('DATA')


    def cancel(self):
        """
        This is the CANCEL behaviour for this job manager. Method ignores
        any data passed as part of the request.
        """
        # Execute the cancel script
        return self.trigger_action_script('CANCEL')

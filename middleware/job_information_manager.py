import os
import posixpath
from mako.template import Template as MakoTemplate
from middleware.job.schema import Template
from middleware.ssh import ssh
import re
import json
from instance.config import *
from werkzeug.exceptions import ServiceUnavailable

# precedence for secrets variables is:
# 1. Via environment varables
# 2. Via instance/config.py
# 3. Via defaults listed below

# defaults
if 'SSH_USR' not in locals():
    SSH_USR = 'test_user'
if 'SSH_HOSTNAME' not in locals():
    SSH_HOSTNAME = 'test_host'
if 'SSH_PORT' not in locals():
    SSH_PORT = 22
if 'SSH_PRIVATE_KEY_PATH' not in locals():
    SSH_PRIVATE_KEY_PATH = None
if 'SSH_PRIVATE_KEY_STRING' not in locals():
    SSH_PRIVATE_KEY_STRING = None
if 'SIM_ROOT' not in locals():
    SIM_ROOT = '/home/test_user'

# Note, os.environ.get() falls back to second argument (instead of None)
SSH_USR = os.environ.get('SSH_USR', SSH_USR)
SSH_HOSTNAME = os.environ.get('SSH_HOSTNAME', SSH_HOSTNAME)
SSH_PORT = os.environ.get('SSH_PORT', SSH_PORT)
SSH_PRIVATE_KEY_PATH = os.environ.get(
    'SSH_PRIVATE_KEY_PATH', SSH_PRIVATE_KEY_PATH)

# an SSH_PRIVATE_KEY_STRING environment variable
# is a multi-line string
# here, we replace the raw r'\n' placeholders
# with line breaks "\n"
SSH_PRIVATE_KEY_STRING = os.environ.get(
    'SSH_PRIVATE_KEY_STRING', SSH_PRIVATE_KEY_STRING)

if isinstance(SSH_PRIVATE_KEY_STRING, str):
    SSH_PRIVATE_KEY_STRING = SSH_PRIVATE_KEY_STRING.replace(r'\n', "\n")

SIM_ROOT = os.environ.get(
    'SIM_ROOT', SIM_ROOT)

SSH_PORT = int(SSH_PORT)

debug_variables = False
if debug_variables:
    print('SSH_USR', SSH_USR)
    print('SSH_HOSTNAME', SSH_HOSTNAME)
    print('SSH_PORT', SSH_PORT)
    print('SSH_PRIVATE_KEY_PATH', SSH_PRIVATE_KEY_PATH)
    print('SSH_PRIVATE_KEY_STRING', SSH_PRIVATE_KEY_STRING)


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

        self.username = SSH_USR
        self.hostname = SSH_HOSTNAME
        self.port = SSH_PORT
        self.simulation_root = SIM_ROOT
        self.private_key_path = SSH_PRIVATE_KEY_PATH
        self.private_key_string = SSH_PRIVATE_KEY_STRING

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
        self.case_dir_label = self.job.case.label.replace(" ", "_")

        self.job_working_directory_name = "{}-{}".format(self.case_dir_label,
                                                         self.job_id)
        self.job_working_directory_path = posixpath.join(
            self.simulation_root,
            self.job_working_directory_name)

    def _extract_parameters(self, families):
        parameters = []
        for family in families:
            parameters.extend(family.parameters)
        return parameters

    def _parameters_to_mako_dict(self, parameters):
        mako_dict = {}
        if parameters:
            for p in parameters:
                mako_dict[p.name] = p.value
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

    def _ssh_connection(self):
        try:
            connection = ssh(
                self.hostname, self.username, self.port,
                private_key_path=self.private_key_path,
                private_key_string=self.private_key_string,
                debug=True)
            return connection
        except Exception:
            # If connection cannot be made, raise a ServiceUnavailble
            # exception that will be passed to API client as a HTTP error
            raise(ServiceUnavailable(
                description="Unable to connect to backend compute resource"))

    def create_job_directory(self, debug=False):
        """
        Create a job directory (All inputs, scripts, templates are transferred
        relative to this location). The job directory is named using the
        following path structure:
            SIM_ROOT/<case.label>-<job.id>
        """
        connection = self._ssh_connection()
        command = "mkdir -p {}".format(self.job_working_directory_path)
        out, err, exit_code = connection.pass_command(command)
        if debug:
            print(out)
        return out, err, exit_code

    def transfer_all_files(self, file_system='unix'):
        """
        Method to copy all needed files to the cluster using a single
        ssh connection.
        """
        connection = self._ssh_connection()
        all_files = []
        all_files.extend(self.script_list)
        all_files.extend(self.inputs_list)
        all_files.extend(self.patched_templates)

        # these are Script, Input and Template model objects
        existing_remote_dirs = [self.job_working_directory_path]

        for file_object in all_files:
            file_full_path = file_object.source_uri
            file_name = os.path.basename(file_full_path)
            if file_object.destination_path:
                dest_path = posixpath.join(
                    self.job_working_directory_path,
                    file_object.destination_path)
            else:  # support {"destination_path": null} in job json
                dest_path = self.job_working_directory_path

            # creating a remote dir may be bandwidth expensive
            # so keep track of what has been created already
            dest_dir = posixpath.dirname(dest_path)
            if dest_dir not in existing_remote_dirs:
                make_remote_dir = "mkdir -p {}".format(dest_dir)
                connection.pass_command(make_remote_dir)
                existing_remote_dirs.append(dest_dir)

            connection.secure_copy(file_full_path, dest_path)

            # convert line endings
            if file_system == 'unix':
                destination_full_path = posixpath.join(dest_path, file_name)
                dos2unix = "dos2unix {}".format(destination_full_path)
                out, err, exit_code = connection.pass_command(dos2unix)

        connection.close_connection()

    def _run_remote_script(self, script_path, call_dir, debug=False):
        """
        Method to run a given script, located in a remote location.
        Set the debug flag to print stdout to the terminal, and to enable
        logging in ./logs/ssh.log
        Shouldnt be called directly.
        """
        connection = self._ssh_connection()
        command = "cd {}; bash {}".format(call_dir, script_path)
        out, err, exit_code = connection.pass_command(command)
        if debug:
            print(out, err, exit_code)
        return out, err, exit_code

    def _run_remote_command(self, command, debug=False):
        """
        Method to run a given command remotely via SSH
        Shouldnt be called directly.
        """
        connection = self._ssh_connection()
        out, err, exit_code = connection.pass_command(command)
        if debug:
            print(out)
        return out, err, exit_code

    def _make_remote_directory(self, relative_path, debug=True):
        """
        Method to make a remote directory.
        """
        connection = self._ssh_connection()
        command = "cd {}; mkdir -p {}".format(
            self.job_working_directory_path, relative_path)
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
        # Imperial PBS Job IDs
        if re.match(r"\d+\.cx1b", stripped_string):
            return stripped_string
        # Azure Torque Job IDs
        if re.match(r"\d+\.science-gateway-cluster", stripped_string):
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
            # script_name = os.path.basename(to_trigger.source_uri)
            # if to_trigger.destination_path:
            #     script_path = posixpath.join(
            #         self.job_working_directory_path,
            #         to_trigger.destination_path)
            # else:  # support {"destination_path": null} in job json
            #     script_path = self.job_working_directory_path

            # call all scripts from the job working directory
            script_path = to_trigger.destination_path
            call_dir = self.job_working_directory_path

            out, err, exit = self._run_remote_script(script_path, call_dir)

            # for "RUN" actions, we need to persist the backend identifier
            # and submission status to the database
            if to_trigger.action == "RUN":
                backend_identifier = self._check_for_backend_identifier(out)
                if backend_identifier:
                    self.job.backend_identifier = backend_identifier
                    self.job.status = "Queued"
                    self.jobs.update(self.job)
            if to_trigger.action in ["DATA", "PROGRESS"]:
                # convert stdout json string to json
                # guard against empty string (for queued jobs)
                if out:
                    out = json.loads(out)

            result = {"stdout": out, "stderr": err, "exit_code": exit}
            return result, 200
        else:
            result = {'message': '{} script not found'.format(action)}
            return result, 400

    def _qstat_status_to_job_status(self, qstat_status):
        if(qstat_status == 'Q' or qstat_status == 'W'):
            # Q: Job is	queued, eligable to run or routed.
            # W: Job is waiting for its	execution time (-a option) to
            #    be reached.
            return "Queued"
        if(qstat_status == 'R'):
            # R: Job is running
            return "Running"
        if(qstat_status == 'C'):
            # C: Job is completed
            return "Complete"
        else:
            return None

    def _qstat_status(self):
        status_cmd = 'qstat {} -x | grep -P -o "<job_state>\K."'.format(
            self.job.backend_identifier)
        out, err, exit = self._run_remote_command(status_cmd)
        # Strip whitespace as we may get a carriage return in the output
        qstat_status = out.strip()
        return qstat_status

    def update_job_status(self):
        # No need to make remote call to qstat if Job is not yet submitted or
        # has already completed
        if(self.job.status not in ["Queued", "Running"]):
            # Leave job status unchanged
            return self.job.status

        # Check current qstat status for job
        qstat_status = self._qstat_status()
        if(qstat_status is not None):
            # If we get a qstat status, try and convert it to a job status
            new_job_status = self._qstat_status_to_job_status(qstat_status)
        else:
            if(self.job.status in ["Submitted", "Queued", "Running"]):
                # If we have a previous backend status confirming the job was
                # on the queue, an empty qstat status means the Job has
                # completed and been removed from the queue.
                # Note: Jobs only stay on the queue for abour 5 mins after they
                # complete
                new_job_status = "Complete"

        if(new_job_status is None):
            # Leave job status unchanged
            new_job_status = self.job.status

        return new_job_status

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
        """
        # Execute the progress script
        return self.trigger_action_script('PROGRESS')

    def data(self):
        """
        This is the DATA behaviour for this job manager. Method ignores
        any data passed as part of the request.
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

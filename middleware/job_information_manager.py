from secrets import *
from mako.template import Template


class job_information_manager():

    def __init__(self, request):

        # gathering the needed info from our secrets file
        self.username = SSH_USR
        self.hostname = SSH_HOSTNAME
        if SSH_PORT:
            self.port = SSH_PORT
        else:
            self.port = 22

        self.job_id = request.json['id']
        self.template_list = request.json['templates']
        self.script_list = request.json['parameters']
        self.parameter_patch = request.json['scripts']

    def _apply_patch(self, template_path, parameters, destination_path):
        template = Template(filename=template_path)
        with open(destination_path, "w") as f:
            f.write(template.render(parameters=parameters))

    def patch_and_transfer(self):
        pass

    def transfer_scripts(self):
        pass

    def run_remote_script(self):
        pass

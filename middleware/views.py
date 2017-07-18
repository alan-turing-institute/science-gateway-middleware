from flask import Flask, jsonify, abort, request, make_response
from flask_httpauth import HTTPBasicAuth
from .ssh import ssh
from secrets import *


import os
from os import makedirs
from os.path import dirname
from os.path import basename


app = Flask(__name__)

# initialise authentication
auth = HTTPBasicAuth()

import f90nml
import json

# TODO LRM (l.mason@imperial.ac.uk) add a configuration system, see http://flask.pocoo.org/docs/0.12/config/
# all cluster paths are relative to this location
# later, make into parameter that can be set from science-gateway-web
simulation_root='/home/vm-admin/simulation'
# simulation_root='tmp'

@auth.get_password
def get_password(username):
    '''
    used to check a username and password against the values in secrets.py
    '''
    if username == USERNAME:
        return PASSWORD
    return None

@auth.error_handler
def unauthorized():
    '''
    output an error message and 401 error code if user/pass are incorrect
    '''
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def ssh_connect(command):
    '''
    Method to set up an ssh connection and send a command to the remote server.
    '''

    # gathering the needed info from our secrets file
    username = SSH_USR
    hostname = SSH_HOSTNAME
    if SSH_PORT:
        port = SSH_PORT
    else:
        port = 22

    connection = ssh(hostname, username, port, debug=True)
    result = connection.pass_command(command)
    connection.close_connection()

    return result


def secure_copy(filename, destination_path):
    '''
    Method to scp a file to cluster.
    '''
    # gathering the needed info from our secrets file
    username = SSH_USR
    hostname = SSH_HOSTNAME
    if SSH_PORT:
        port = SSH_PORT
    else:
        port = 22

    connection = ssh(hostname, username, port, debug=True)
    connection.secure_copy(filename, destination_path)
    connection.close_connection()
    # return result


@app.route('/post', methods=['POST'])
@auth.login_required
def recieve_information():
    '''
    http post method to append data to the stored json.
    to pass a json into the app use the following command:
    curl -u <username>:<password> -i -H "Content-Type: application/json"
    -X POST -d '{"length":5, "width": 10}' http://localhost:5000/post
    '''
    if not request.json:
        abort(400)
    if 'length' not in request.json and 'width' not in request.json:
        abort(400)
    input_data = {
        'length': request.json['length'],
        'width': request.json['width'],
    }
    result = workflow(input_data)
    return result, 201

# TODO LRM (l.mason@imperial.ac.uk): generalise to templating patch system,
# i.e. generalise to a system that is not f90 specific

def apply_patch(template_path, parameters, destination_path):
    f90nml.patch(template_path, parameters, destination_path)

def patch_and_transfer_template_files(template_list, parameter_patch):
    '''
    Apply patch to all template files
    '''
    for template in template_list:
        template_file = template["source_uri"]
        template_filename = basename(template_file)

        destination_path = os.path.join(simulation_root, template["destination_path"])

        tmp_path = os.path.join('tmp', template["destination_path"])
        tmp_file = os.path.join(tmp_path,template_filename)
        makedirs(tmp_path, exist_ok=True)

        apply_patch(template_file, parameter_patch, tmp_file)
        secure_copy(tmp_file, destination_path)

def transfer_files(object_list):
    '''
    Method to copy multiple files to cluster using single SSHClient connection
    '''
    # gathering the needed info from our secrets file
    username = SSH_USR
    hostname = SSH_HOSTNAME
    if SSH_PORT:
        port = SSH_PORT
    else:
        port = 22

    connection = ssh(hostname, username, port, debug=True)

    for file_object in object_list:
        file_full_path = file_object["source_uri"]
        destination_path = os.path.join(simulation_root, file_object["destination_path"])
        secure_copy(file_full_path, destination_path)
    connection.close_connection()

def run_remote_script(script_name, remote_path, debug=True):
    command = "cd {}; bash {}".format(remote_path, script_name)
    out = ssh_connect(command)
    if debug:
        print(out)

# currently exposed method, later make private and call from /run
# rename to /api/run if necessary
@app.route('/setup', methods=['POST'])
@auth.login_required
def setup():
    '''
    '''

    # TODO build data structure here with full remote path information, so that
    # generating full paths is a once only operation

    input_data = {
        'id': request.json['id'],
        'templates': request.json['templates'],
        'parameters': request.json['parameters'],
        'scripts': request.json['scripts']
    }

    template_list = input_data["templates"]
    script_list = input_data["scripts"]
    parameter_patch = input_data["parameters"]

    patch_and_transfer_template_files(template_list, parameter_patch)
    transfer_files(script_list)

    for script in script_list:
        script_name = basename(script["source_uri"])
        remote_location = os.path.join(simulation_root, script["destination_path"])
        run_remote_script(script_name, remote_location)

    # TODO add an actual check on "success"
    result = jsonify({"success":"true", "message": "patch applied"})
    return result, 201

@app.errorhandler(404)
def not_found(error):
    '''
    handles 404 errors gracefully
    '''
    return make_response(jsonify({'error': 'Not found'}), 404)

def workflow(input_data):
    '''
    Wrapper to chain the various methods together.
    '''
    command = build_command(input_data)
    return ssh_connect(command)


def build_command(input_data):
    '''
    Currently takes the input json data from the POST request and parses
    it into our simple bash command. Eventually this method will parse the
    frontend jsons and output commands for BEMPP
    '''
    # a simple command that multiplies 2 numbers
    return 'echo "$(({0} * {1}))"'.format(input_data['length'],
                                          input_data['width'])

if __name__ == '__main__':
    app.run()

from flask import Flask, jsonify, abort, request, make_response
from flask_httpauth import HTTPBasicAuth
from .ssh import ssh
from secrets import *

app = Flask(__name__)

# initialise authentication
auth = HTTPBasicAuth()


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

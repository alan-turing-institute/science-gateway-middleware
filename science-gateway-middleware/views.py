from flask import Flask, jsonify, abort, request, make_response
from flask_httpauth import HTTPBasicAuth
from secrets import *

# simple json, will be replaced by the incoming data from the frontend
middle = [
    {
        'id': 1,
        'length': 2,
    }
]


app = Flask(__name__)

# initialise authentication
auth = HTTPBasicAuth()


# used to check a username and password against the values in secrets.py
@auth.get_password
def get_password(username):
    if username == USERNAME:
        return PASSWORD
    return None


# output an error message and 401 error code if user/pass are incorrect
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


# basic homepage at top of domain, not needed in final app but good for testing
@app.route("/")
def hello():
    return "Hello World!"


# http get method to return contents of the json message, defined above
@app.route('/middle/api/v1.0/get', methods=['GET'])
@auth.login_required
def get_information():
    return jsonify({'message': middle})


# http post method to append data to the stored json.
# to pass the json {"length":5} into the app use the following command:
# curl -u <username>:<password> -i -H "Content-Type: application/json"
# -X POST -d '{"length":5}' http://localhost:5000/middle/api/v1.0/value

@app.route('/middle/api/v1.0/value', methods=['POST'])
@auth.login_required
def recieve_information():
    if not request.json or 'length' not in request.json:
        abort(400)
    tmp = {
        'id': middle[-1]['id'] + 1,
        'length': request.json['length'],
    }
    middle.append(tmp)
    return jsonify({'message': middle}), 201


# handles 404 errors gracefully
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run()

from flask import Flask, jsonify, abort, request
from flask_httpauth import HTTPBasicAuth
from flask import make_response
from secrets import *

middle = [
    {
        'id': 1,
        'length': 2,
    }
]


app = Flask(__name__)


auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == USERNAME:
        return PASSWORD
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/middle/api/v1.0/getter', methods=['GET'])
@auth.login_required
def get_information():
    return jsonify({'message': middle})


#curl -i -H "Content-Type: application/json" -X POST -d '{"length":5}' http://localhost:5000/middle/api/v1.0/value

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


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run()

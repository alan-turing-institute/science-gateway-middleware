# science-gateway-middleware

[![Build Status](https://travis-ci.org/alan-turing-institute/science-gateway-middleware.svg?branch=master)](https://travis-ci.org/alan-turing-institute/science-gateway-middleware)
[![Build Status](https://ci.appveyor.com/api/projects/status/github/alan-turing-institute/science-gateway-middleware?branch=master)](https://ci.appveyor.com/api/projects/status/github/alan-turing-institute/science-gateway-middleware)

## Overview

Currently this is a skeleton app that is designed to take values via `HTTP POST`, build a bash command to multiply them together and run that command via ssh on a remote server.


## Deployment

This code is tested on `python 3.6` and all dependencies can be installed via `pip`:

```
pip install -r requirements.txt
```

At present this app uses a `secrets.py` file to store login details. For obvious reasons this is not committed with the rest of the code, but can be created locally. The code expects a `secrets.py` file placed in the root of the directory with the following variables:

```
USERNAME = "<a username>"
PASSWORD = "<a password>"
SSH_USR = "<username to connect to remote server>"
SSH_HOSTNAME = "<ip address of server to ssh into>"
SSH_PORT = <optional port to connect via, defaults to 22>
```

`USERNAME` and `PASSWORD` are set to provide a mock up of http password authentication which is used to restrict access to the `POST` method.

The `SHH_*` variables will need to point to `science-gateway-cluster` but at present I have been testing this via one of UCL's servers. The ssh code assumes that you already have ssh keys configured on the machine where the app is running, and has limited error handling if this is not the case.

### Local deployment

```
git clone git@github.com:alan-turing-institute/science-gateway-middleware.git
cd science-gateway-middleware/middleware
export FLASK_APP=views.py
export FLASK_DEBUG=1
flask run
```

## Usage

This app is designed to provide an example of how the middleware will interact with the front end and the cluster. The app currently receives two values, `length` and `width` as a `json`, eg:

```
{"length":5, "width": 10}
```

via an `HTTP POST` request:

```
curl -u <username>:<password> -i -H "Content-Type: application/json" -X POST -d '{"length":5, "width": 10}' http://localhost:5000/post
```

Where in this case the app is running on a local machine for testing and username and password must match the `USERNAME` and `PASSWORD` values in the `secrets.py` file discussed above.

The flask app parses the length and width values out of the json and constructs a simple bash command to multiply them together:

```
echo "$(({5} * 10))"
```

This command is sent via ssh to the server detailed in `secrets.py`, which executes the command, and returns the product to the flask app, where it is returned as the result of the original `POST` request:

```
HTTP/1.0 201 CREATED
Content-Type: text/html; charset=utf-8
Content-Length: 3
Server: Werkzeug/0.12.2 Python/3.6.1
Date: Mon, 26 Jun 2017 10:49:31 GMT

50
```

## Testing

Tests can be run via `python -m pytest`.

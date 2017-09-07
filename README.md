# science-gateway-middleware

[![Build Status](https://travis-ci.org/alan-turing-institute/science-gateway-middleware.svg?branch=master)](https://travis-ci.org/alan-turing-institute/science-gateway-middleware)
[![Build Status](https://ci.appveyor.com/api/projects/status/github/alan-turing-institute/science-gateway-middleware?branch=master)](https://ci.appveyor.com/api/projects/status/github/alan-turing-institute/science-gateway-middleware)

## Overview

Currently this is a skeleton app that is designed to take values via `HTTP POST`, build a bash command to multiply them together and run that command via ssh on a remote server.

## Local deployment 

This code is tested on `python 3.4` and all dependencies can be installed via `pip`:

```
pip install -r requirements.txt
```

At present this app uses a `config.py` file to store login details. For obvious reasons this is not committed with the rest of the code, but can be created locally. The code expects a `config.py` file placed in a root-level `instance` of the directory with the following variables:

```
USERNAME = "<a username>"
PASSWORD = "<a password>"
SSH_USR = "<username to connect to remote server>"
SSH_HOSTNAME = "<ip address of server to ssh into>"
SSH_PORT = <optional port to connect via, defaults to 22>
# SSH_PRIVATE_KEY_PATH = None
SSH_PRIVATE_KEY_PATH = "keys/development"  # where development is a private RSA key

# SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

The `SHH_*` variables will need to point to `science-gateway-cluster` but at present I have been testing this via one of UCL's servers. The ssh code assumes that you already have ssh keys configured on the machine where the app is running, and has limited error handling if this is not the case.

The middleware can be hosted locally on `localhost` for testing via the `middleware/app.py` entry point. To achieve this, run the following command:

```shell
./run_test.sh
```

Similarly, the production config file checked into source control can be tested using `./run_production.sh`. However, note that the same `instance/config.py` will be used in all cases, so it will nbot be a true test of production


## Azure deployment

To create an MS Azure Web App Service run the following sequence of commands. First, choose a name for the app (note, the resource group, app service plan and web app will all share this name, but unique names could be set for each if needed).

```shell
APP_NAME=Science-Gateway-Middleware
```

Set a username and password for the Web App Service:

```
az login
az webapp deployment user set --user-name <username> --password <password>
```

Create the Azure web app:

```shell
az group create --name $APP_NAME --location westeurope
az appservice plan create --name $APP_NAME --resource-group $APP_NAME --sku S1  # use S1 or higher for access to development slots
az webapp create --name $APP_NAME --resource-group $APP_NAME --plan $APP_NAME
az webapp config set --python-version 3.4 --name $APP_NAME --resource-group $APP_NAME # set python version
az webapp config appsettings set --name $APP_NAME --resource-group $APP_NAME --settings APP_CONFIG_FILE=../config/production.py # set flask environment variables
```

Configure web app environment variables.

```shell
APP_NAME=Science-Gateway-Middleware
APP_SLOT=dev

az webapp config appsettings set --name $APP_NAME --resource-group $APP_NAME --slot  $APP_SLOT --settings SSH_USR=<ssh-user>

az webapp config appsettings set --name $APP_NAME --resource-group $APP_NAME --slot  $APP_SLOT --settings SSH_HOSTNAME=<ssh-hostname>

az webapp config appsettings set --name $APP_NAME --resource-group $APP_NAME --slot  $APP_SLOT --settings SSH_PORT=22

az webapp config appsettings set --name $APP_NAME --resource-group $APP_NAME --slot  $APP_SLOT --settings SIM_ROOT=<sim-root>

az webapp config appsettings set --name $APP_NAME --resource-group $APP_NAME --slot  $APP_SLOT --settings SSH_PRIVATE_KEY_STRING=<private-key-string>
```

The `develop` branch will deploy to a development "slot" on Azure via the following branch-specific `.travis.yml`settings:

```yaml
deploy:
  - provider: azure_web_apps
    verbose: true
    skip_cleanup: false
    on: develop
    slot: science-gateway-middleware-dev
```

The `staging` branch will deploy to a staging "slot" on Azure via the following branch-specific `.travis.yml`settings:

```yaml
deploy:
  - provider: azure_web_apps
    verbose: true
    skip_cleanup: false
    on: staging
    slot: science-gateway-middleware-staging
```

Manual deployment to Azure is possible via `dpl`:

```
sudo gem install dpl
```

For example, run the following to deploy to the Azure dev slot:

```
export AZURE_WA_PASSWORD=<password>
export AZURE_WA_USERNAME=<user-name>
export AZURE_WA_SITE=science-gateway-middleware
export AZURE_WA_SLOT=science-gateway-middleware-dev
dpl --provider=AzureWebApps --verbose
```



Any un-committed files can be added using using ftp. The ftp address is available via `App Service > Properties` in Azure portal. An example ftp credentials are:

```
server address: ftps://<address-details>.ftp.azurewebsites.windows.net
user: Science-Gateway-Middleware\<username>
```

## Testing

Tests can be run via `python -m pytest`.

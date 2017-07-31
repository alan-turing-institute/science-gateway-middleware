import os
import pytest
from lxml import etree
from middleware.app import app_wrapper


@pytest.fixture(autouse=True)
def app_config(monkeypatch):
    '''
    monkeypatch the environment variable so the tests will run on Travis
    '''
    monkeypatch.setenv('APP_CONFIG_FILE', '../config/travis.py')


def parse_web_config(app):
    '''
    Get the value stored in the variable WSGI_ALT_VIRTUALENV_HANDLER in
    the file web.config
    '''
    web_config_location = build_web_config_path(app)
    doc = etree.parse(web_config_location)

    keys = doc.xpath('/configuration/appSettings/add/@key')
    values = doc.xpath('/configuration/appSettings/add/@value')

    key_to_find = 'WSGI_ALT_VIRTUALENV_HANDLER'

    # Check that the key exists, and if it does, return its value
    if key_to_find in keys:
        return values[keys.index(key_to_find)]
    else:
        return None


def build_web_config_path(app):
    '''
    Build the path to where the web.config file should be
    '''
    rootpath = os.path.split(app.root_path)[0]
    return os.path.join(rootpath, 'web.config')


class TestApp(object):

    def test_app(self):
        '''
        Simple test of app.py, checks that the app is built correctly
        using the expected factory.
        '''
        app = app_wrapper()

        assert app.name == 'middleware.factory'

    def test_web_config_exists(self):
        '''
        Check that a web config file exists for azure
        '''
        app = app_wrapper()
        web_config_location = build_web_config_path(app)

        assert os.path.exists(web_config_location) is True

    def test_azure_params(self):
        '''
        Check the contents of web.config to ensure that the
        app will deploy correctly on azure as well as locally.
        '''
        app = app_wrapper()
        WSGI_ALT = parse_web_config(app)
        basename = app.name.split('.')[0]

        assert WSGI_ALT == '{}.app.app'.format(basename)

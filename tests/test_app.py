import os
import pytest
import xml.etree.cElementTree as ET
from middleware.factory import create_app
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.job.sqlalchemy_repository import CaseRepositorySqlAlchemy
from flask import Flask
from middleware.database import db as _db


CONFIG_NAME = "test"
TEST_DB_URI = 'sqlite://'


def parse_web_config(app):
    '''
    Get the value stored in the variable WSGI_ALT_VIRTUALENV_HANDLER in
    the file web.config
    '''
    web_config_location = build_web_config_path(app)
    doc = ET.ElementTree(file=web_config_location)
    key_to_find = 'WSGI_ALT_VIRTUALENV_HANDLER'
    element = doc.find('appSettings/add[@key="{}"]'.format(key_to_find))

    if element is not None:
        return element.attrib['value']
    else:
        return None


def build_web_config_path(app):
    '''
    Build the path to where the web.config file should be
    '''
    rootpath = os.path.split(app.root_path)[0]
    return os.path.join(rootpath, 'web.config')


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test Flask app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.test")
    _db.init_app(app)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database"""
    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Function-wide SQLAlchemy session for each test"""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={}, expire_on_commit=True)
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


class TestApp(object):

    def test_app(self, session):
        '''
        Simple test of app.py, checks that the app is built correctly
        using the expected factory.
        '''
        app = create_app(CONFIG_NAME,
                         case_repository=CaseRepositorySqlAlchemy(session),
                         job_repository=JobRepositorySqlAlchemy(session))
        assert app.name == 'middleware.factory'

    def test_web_config_exists(self, session):
        '''
        Check that a web config file exists for azure
        '''
        app = create_app(CONFIG_NAME,
                         case_repository=CaseRepositorySqlAlchemy(session),
                         job_repository=JobRepositorySqlAlchemy(session))
        web_config_location = build_web_config_path(app)

        assert os.path.exists(web_config_location) is True

    def test_azure_params(self, session):
        '''
        Check the contents of web.config to ensure that the
        app will deploy correctly on azure as well as locally.
        '''
        app = create_app(CONFIG_NAME,
                         case_repository=CaseRepositorySqlAlchemy(session),
                         job_repository=JobRepositorySqlAlchemy(session))
        WSGI_ALT = parse_web_config(app)
        basename = app.name.split('.')[0]

        assert WSGI_ALT == '{}.app.app'.format(basename)

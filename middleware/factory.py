from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.job.sqlalchemy_repository import CaseRepositorySqlAlchemy
from middleware.job.api import (JobApi, JobsApi, SetupApi, RunApi, ProgressApi,
                                CancelApi, CaseApi, CasesApi)
from middleware.database import db, ma
from middleware.job.schema import CaseSchema
import json


def json_to_case_list(json_filename):
    case_list = []
    with open(json_filename) as data_file:
        data = json.load(data_file)
        for case_json in data:
            case = CaseSchema().make_case(case_json)
            case_list.append(case)
    return case_list


def create_app(config_name,
               case_repository=None,
               job_repository=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import environment specific variables from the supplied
    # configuration
    app.config.from_object("config.{}".format(config_name))

    # Load non-source controlled config variables from the instance folder
    # if present (fails silently if not present)
    app.config.from_pyfile("config.py", silent=True)

    # Load the URI stems from the base config
    from config.base import URI_STEMS

    # NOTE: Temporary configuration code lives here while we refactor
    # to make data store dependencies purely set in configuration
    # NOTE: Keep app._job_repository as we'll need this for our API tests when
    # we are no longer injecting the repo at app creation

    # determine repository types
    if case_repository is None:
        case_repository_type = None
    elif isinstance(case_repository, CaseRepositorySqlAlchemy):
        case_repository_type = 'sqlalchemy'
    else:
        case_repository_type = 'other'

    if job_repository is None:
        job_repository_type = None
    elif isinstance(job_repository, JobRepositorySqlAlchemy):
        job_repository_type = 'sqlalchemy'
    else:
        job_repository_type = 'other'

    # define default repository type (used if no repo is specified)
    def default_case_repository():
        case_repository = CaseRepositorySqlAlchemy(db.session)
        return case_repository

    def default_job_repository():
        job_repository = JobRepositorySqlAlchemy(db.session)
        return job_repository

    def configure_sqlalchemy(app):
        db.init_app(app)
        ma.init_app(app)
        db.create_all(app=app)

    if (case_repository_type is None) or (job_repository_type is None):
        configure_sqlalchemy(app)
    elif (case_repository_type is 'sqlalchemy') or \
         (job_repository_type is 'sqlalchemy'):
        configure_sqlalchemy(app)

    # set the case repository
    if case_repository_type is None:
        case_repository = default_case_repository()
    elif case_repository_type == 'sqlalchemy':
        case_repository._session = db.session
    else:
        raise NotImplementedError("Case repository type not implemented")

    # set the job repository
    if job_repository_type is None:
        job_repository = default_job_repository()
    elif job_repository_type == 'sqlalchemy':
        job_repository._session = db.session
    else:
        raise NotImplementedError("Job repository type not implemented")

    # Assign the repo to the app for easy access
    app._case_repository = case_repository
    app._job_repository = job_repository

    if app.config['LOAD_CASES']:
        cases_json_filename = './resources/cases/blue_cases.json'
        case_list = json_to_case_list(cases_json_filename)
        with app.app_context():
            for case in case_list:
                app._case_repository.create(case)

    api = Api(app)

    api.add_resource(JobApi, '{}/<string:job_id>'.format(URI_STEMS['jobs']),
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(JobsApi, URI_STEMS['jobs'],
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(CasesApi, URI_STEMS['cases'],
                     resource_class_kwargs={'case_repository':
                                            app._case_repository})

    api.add_resource(CaseApi, '{}/<string:case_id>'.format(URI_STEMS['cases']),
                     resource_class_kwargs={'case_repository':
                                            app._case_repository})

    api.add_resource(SetupApi, '{}/<string:job_id>'.format(URI_STEMS['setup']),
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(RunApi, '{}/<string:job_id>'.format(URI_STEMS['run']),
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(ProgressApi,
                     '{}/<string:job_id>'.format(URI_STEMS['progress']),
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(CancelApi,
                     '{}/<string:job_id>'.format(URI_STEMS['cancel']),
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    return app

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.job.api import (JobApi, JobsApi, SetupApi, RunApi, ProgressApi,
                                CancelApi, CaseApi, CasesApi)
from middleware.database import db, ma


def create_app(config_name, job_repository=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import environment specific variables from the supplied
    # configuration
    app.config.from_object("config.{}".format(config_name))

    # Load non-source controlled config variables from the instance folder
    # if present (fails silently if not present)
    app.config.from_pyfile("config.py", silent=True)

    # Load the path to the cases file from the base config
    from config.base import cases_path

    # TODO: Remove the conditional here. This is only to let us still inject
    # job_repository explicitly while we refactor to make data store dependency
    # purely set in configuration
    # NOTE: We'll need to add
    #   job_repository = JobRepositorySqlAlchemy(db.session)
    # Add it after db.create_all() to be safe.
    # NOTE: Also remove the job_repository injection from factory.py
    # NOTE: Keep app._job_repository as we'll need this for our API tests when
    # we are no longer injecting the repo at app creation
    if job_repository is None:
        # If not repo provided, nitialise new SQLAlchemy backed repository
        db.init_app(app)
        ma.init_app(app)
        db.create_all(app=app)
        job_repository = JobRepositorySqlAlchemy(db.session)
    elif isinstance(job_repository, JobRepositorySqlAlchemy):
        # If SQLAlchemy repo provided, preserve session from provided repo
        db.init_app(app)
        ma.init_app(app)
        db.create_all(app=app)
        job_repository._session = db.session
    # In all cases assign the repo to the app for easy access
    app._job_repository = job_repository

    api = Api(app)

    api.add_resource(JobApi, '/api/job/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    api.add_resource(JobsApi, '/api/job',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(SetupApi, '/api/setup/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(RunApi, '/api/run/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(ProgressApi, '/api/progress/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(CancelApi, '/api/cancel/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(CasesApi, '/api/cases/',
                     resource_class_kwargs={'cases_path': cases_path})

    api.add_resource(CaseApi, '/api/cases/<string:case_id>',
                     resource_class_kwargs={'cases_path': cases_path})

    return app

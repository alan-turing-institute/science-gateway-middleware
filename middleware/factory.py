from flask import Flask
from flask_restful import Api
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.job.api import JobApi, JobsApi
from middleware.database import db, ma


def create_app(config_name, job_repository):
    app = Flask(__name__, instance_relative_config=True)

    # Import environment specific variables from the supplied
    # configuration
    app.config.from_object("config.{}".format(config_name))

    # Load non-source controlled config variables from the instance folder
    # if present (fails silently if not present)
    app.config.from_pyfile("config.py", silent=True)

    # TODO: Remove the conditional here. This is only to let us still inject
    # job_repository explicitly while we refactor to make data store dependency
    # purely set in configuration
    # NOTE: We'll need to add
    #   job_repository = JobRepositorySqlAlchemy(db.session)
    # Add it after db.create_all() to be safe.
    # NOTE: Also remove the job_repository injection from factory.py
    # NOTE: Keep app._job_repository as we'll need this for our API tests when
    # we are no longer injecting the repo at app creation
    if isinstance(job_repository, JobRepositorySqlAlchemy):
        db.init_app(app)
        ma.init_app(app)
        db.create_all(app=app)
        # If the provided repository has not had a session specified, then
        # use the app db session.
        # NOTE: We don't overwrite any existing specified session as we want to
        # be able to pass in a session during testing
        if job_repository._session is None:
            job_repository._session = db.session

    app._job_repository = job_repository

    api = Api(app)

    api.add_resource(JobApi, '/job/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    api.add_resource(JobsApi, '/job',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    return app

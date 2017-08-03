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
    if isinstance(job_repository, JobRepositorySqlAlchemy):
        db.init_app(app)
        ma.init_app(app)
        db.create_all(app=app)
        app._db = db
        app._ma = ma

    app._job_repository = job_repository

    api = Api(app)

    api.add_resource(JobApi, '/job/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    api.add_resource(JobsApi, '/job',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    return app

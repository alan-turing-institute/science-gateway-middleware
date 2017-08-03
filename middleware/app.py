import os
import sys

# # Use in-memory repository
# from middleware.job.inmemory_repository import JobRepositoryMemory
# job_repository = JobRepositoryMemory()
# app = create_app(job_repository)


# Use in-memory SQL repository
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api
from middleware.core import db
from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.job.sqlalchemy_repository import JobRepositorySqlAlchemy
from middleware.job.api import JobApi, JobsApi


def create_app(config_name, job_repository):
    app = Flask(__name__, instance_relative_config=True)

    # Import environment specific variables from the supplied
    # configuration
    app.config.from_object("config.{}".format(config_name))

    # Load non-source controlled config variables from the instance folder
    # if present (fails silently if not present)
    app.config.from_pyfile("config.py", silent=True)

    if isinstance(job_repository, JobRepositorySqlAlchemy):
        db = SQLAlchemy(app)
        ma = Marshmallow(app)

    app._job_repository = job_repository

    api = Api(app)

    api.add_resource(JobApi, '/job/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    api.add_resource(JobsApi, '/job',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    return app


# job_repository = JobRepositorySqlAlchemy()
# app = create_app(job_repository)

#
#
# db.init_app(app)
# db.create_all(app=app)
# ma = Marshmallow(app)


if __name__ == "__main__":
    config_name = os.environ.get('APP_CONFIG_NAME')
    if not config_name:
        config_name = 'test'
    job_repository = JobRepositoryMemory()
    app = create_app(config_name, job_repository)
    app.run()

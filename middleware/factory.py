from flask import Flask
from flask_restful import Api
from middleware.job.api import JobApi, JobsApi, RUNApi


def create_app(job_repository):
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_object('config.default')

    # Load the configuration from the instance folder
    app.config.from_pyfile('config.py')

    # Load the file specified by the APP_CONFIG_FILE environment variable
    # Variables defined here will override those in the default configuration
    app.config.from_envvar('APP_CONFIG_FILE')

    app._job_repository = job_repository
    api = Api(app)

    api.add_resource(JobApi, '/job/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})
    api.add_resource(JobsApi, '/job',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(SETUPApi, '/SETUP/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(RUNApi, '/RUN/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(PROGRESSApi, '/PROGRESS/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    api.add_resource(CANCELApi, '/CANCEL/<string:job_id>',
                     resource_class_kwargs={'job_repository':
                                            app._job_repository})

    return app

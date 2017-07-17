from flask import Flask
from flask_restful import Api
from middleware.job.common import JobApi, JobsApi
from middleware.job.inmemory import JobRepositoryMemory


def create_app(job_repository):
    app = Flask("app")
    app.job_repository = job_repository
    api = Api(app)

    api.add_resource(JobApi, '/job/<string:job_id>',
                     resource_class_kwargs={'job_repository': app.job_repository})
    api.add_resource(JobsApi, '/jobs',
                     resource_class_kwargs={'job_repository': app.job_repository})
    return app


if __name__ == "__main__":
    # Use in-memory repository for now.
    # TODO: Make this configurable
    job_repository = JobRepositoryMemory()
    # Create an app backed by the appropriate repository
    app = create_app(job_repository)
    app.run()

from middleware.factory import create_app
from middleware.job.inmemory_repository import JobRepositoryMemory


def app_wrapper():
    # Use in-memory repository for now.
    job_repository = JobRepositoryMemory()
    # Create an app backed by the appropriate repository
    app = create_app(job_repository)

    return app

if __name__ == "__main__":
    app = app_wrapper()
    app.run()

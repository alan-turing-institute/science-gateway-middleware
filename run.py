import os
from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.factory import create_app


def app_wrapper():
    # Use in-memory repository for now.
    # TODO: Make this configurable
    job_repository = JobRepositoryMemory()
    # Create an app backed by the appropriate repository
    app = create_app(job_repository)
    return app


# Only lauch the app if called from the run bash script
# Stops this app being launched by pytest, causing the tests to stall
if os.getenv('APP_RUN_FLAG', None):
    app_wrapper().run()

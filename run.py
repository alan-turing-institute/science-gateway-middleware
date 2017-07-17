from middleware.job.inmemory import JobRepositoryMemory
from middleware.app import create_app


# Use in-memory repository for now.
# TODO: Make this configurable
job_repository = JobRepositoryMemory()
# Create an app backed by the appropriate repository
app = create_app(job_repository)
app.run()

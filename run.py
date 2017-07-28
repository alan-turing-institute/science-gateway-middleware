from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.factory import create_app

# Use in-memory repository for now.
# TODO: Make this configurable
job_repository = JobRepositoryMemory()
# Create an app backed by the appropriate repository
app = create_app(job_repository)
app.run()

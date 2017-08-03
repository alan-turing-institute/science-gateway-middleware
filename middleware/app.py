from middleware.factory import create_app

# Use in-memory repository
from middleware.job.inmemory_repository import JobRepositoryMemory
job_repository = JobRepositoryMemory()

# Create an app backed by the appropriate repository
app = create_app(job_repository)

if __name__ == "__main__":
    app.run()

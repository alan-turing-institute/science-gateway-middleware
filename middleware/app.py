from middleware.factory import create_app
from middleware.job.inmemory_repository import JobRepositoryMemory

# Use in-memory repository for now.
job_repository = JobRepositoryMemory()
# Create an app backed by the appropriate repository
app = create_app(job_repository)

if __name__ == "__main__":
    app.run()

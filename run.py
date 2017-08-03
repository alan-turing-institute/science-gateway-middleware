from middleware.factory import create_app

# Create an app backed by the appropriate repository

# # Use in-memory repository
# from middleware.job.inmemory_repository import JobRepositoryMemory
# job_repository = JobRepositoryMemory()
# app = create_app(job_repository)
# app.run()

# Use in-memory SQL repository
from middleware.core import db
from middleware.job.inmemory_repository_sql import JobRepositoryMemorySQL
job_repository = JobRepositoryMemorySQL()
app = create_app(job_repository)
db.init_app(app)
db.create_all(app=app)
app.run()

from flask import Flask
from flask_restful import Api
from middleware.job.api import JobApi, JobsApi
from middleware.job.inmemory_repository import JobRepositoryMemory
from middleware.factory import create_app

# Use in-memory repository for now.
job_repository = JobRepositoryMemory()
# Create an app backed by the appropriate repository
app = create_app(job_repository)
app.run()

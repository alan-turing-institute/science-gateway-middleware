import os
from middleware.factory import create_app
from middleware.job.inmemory_repository import JobRepositoryMemory


if __name__ == "__main__":
    config_name = os.environ.get('APP_CONFIG_NAME')
    if not config_name:
        config_name = 'test'
    job_repository = JobRepositoryMemory()
    app = create_app(config_name, job_repository)
    app.run()

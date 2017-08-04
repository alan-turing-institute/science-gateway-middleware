import os
from middleware.factory import create_app
from middleware.job.inmemory_repository import JobRepositoryMemory

config_name = os.environ.get('APP_CONFIG_NAME')
if not config_name:
    config_name = 'test'
repo = JobRepositoryMemory()
app = create_app(config_name, repo)
app.run()

import os
from middleware.factory import create_app

config_name = os.environ.get('APP_CONFIG_NAME')
if not config_name:
    config_name = 'test'
app = create_app(config_name)

if __name__ == "__main__":
    app.run()

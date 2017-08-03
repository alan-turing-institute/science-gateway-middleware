export FLASK_APP=run.py
export APP_CONFIG_FILE=../config/travis.py
export APP_RUN_FLAG=1
mkdir -p instance
cd instance
touch config.py
cd ..
flask run.py

export FLASK_APP=run.py
export APP_CONFIG_FILE=../config/travis.py
mkdir -p instance
cd instance
touch config.py
cd ..
flask run.py

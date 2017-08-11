from config.base import *

# This config is configured for running local tests
TESTING = True
DEBUG = True

# Use in-memory SQLlite DB for testing
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# The path to the cases file
cases_path = './resources/cases/blue.json'

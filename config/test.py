from config.base import *

# This config is configured for running local tests
TESTING = True
DEBUG = True

# Use in-memory SQLlite DB for testing
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Load cases from resources json file
LOAD_CASES = False
LOAD_DEVELOPMENT_CASES = False

# load private key from "keys" directory
LOAD_DEVELOPMENT_PRIVATE_KEY = False

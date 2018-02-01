# This contains the standard config that all other configs inherit from

# A dictionary of URI stems for the various API actions
URI_STEMS = {'jobs': '/api/jobs',
             'setup': '/api/setup',
             'run': '/api/run',
             'cancel': '/api/cancel',
             'progress': '/api/progress',
             'store': '/api/store',
             'data': '/api/data',
             'cases': '/api/cases',
             'thumbnails': '/assets/thumbnails'}

MIDDLEWARE_URL = "https://science-gateway-middleware.azurewebsites.net"
# MIDDLEWARE_URL = "http://localhost:5000"

MIDDLEWARE_ONLY_JOB_FIELDS = [
    "status",
    "creation_datetime",
    "start_datetime",
    "end_datetime",
    "backend_identifier"
]

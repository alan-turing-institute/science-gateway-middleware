# This contains the standard config that all other configs inherit from

# The path to the cases file
case_summaries_path = './resources/cases/blue_case_summaries.json'
cases_path = './resources/cases/blue_cases.json'

# A dictionary of URI stems for the various API actions
URI_Stems = {'job': '/api/jobs',
             'setup': '/api/setup',
             'run': '/api/run',
             'cancel': '/api/cancel',
             'progress': '/api/progress',
             'cases': '/api/cases'}

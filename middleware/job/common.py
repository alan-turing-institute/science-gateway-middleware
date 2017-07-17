from flask_restful import Resource, abort, request


class JobApi(Resource):
    '''API for reading (GET), amending (POST/PATCH) and deleting (DELETE)
    individual jobs'''
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def abort_if_not_found(self, job_id):
        if not self.jobs.exists(job_id):
            abort(404, message="Job {} not found".format(job_id))

    def get(self, job_id):
        self.abort_if_not_found(job_id)
        job = self.jobs.get_by_id(job_id)
        return job, 200, {'Content-Type': 'application/json'}


class JobsApi(Resource):
    '''API for listing a collection of jobs (GET) and creating a new
    individual job (POST)'''
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def post(self):
        job = request.json
        if job is None:
            abort(400, message="Message body could not be parsed as JSON")
        else:
            job_id = job.get("id")
            if self.jobs.exists(job_id):
                abort(409, message="Job with ID {} already exists".format(job_id))
            else:
                job = self.jobs.create(job)
                return job, 200, {'Content-Type': 'application/json'}

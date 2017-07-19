import os
from flask_restful import Resource, abort, request
from os.path import basename
from middleware.job.model import is_valid_job_json
from middleware.job_information_manager import job_information_manager as JIM


class JobApi(Resource):
    '''API for reading (GET), amending (PUT/PATCH) and deleting (DELETE)
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

    def put(self, job_id):
        # Require Job to exist in order to amend it
        job_old = self.jobs.get_by_id(job_id)
        if job_old is None:
            self.abort_if_not_found(job_id)
        # Get Job JSON if present
        job_new = request.json
        if job_new is None:
            abort(400, message="Message body could not be parsed as JSON")
        # Require valid Job JSON
        if not is_valid_job_json(job_new):
            abort(400, message="Message body is not valid Job JSON")
        # Check job_id route parameter consistent with JSON data
        job_id_json = job_new.get("id")
        if job_id != job_id_json:
            abort(409, message="Job ID in URL ({}) does not match job "
                               "ID in message JSON ({}).".format(job_id,
                                                                 job_id_json))
        # Try and update Job
        updated_job = self.jobs.update(job_new)
        if updated_job is None:
            abort(404, message="Job {} not found".format(job_id_json))
        else:
            return updated_job, 200, {'Content-Type': 'application/json'}

    def delete(self, job_id):
        # Require job to exist in order to delete it
        job = self.jobs.get_by_id(job_id)
        if job is None:
            self.abort_if_not_found(job_id)
        # Delete job
        self.jobs.delete(job_id)
        deleted_job = self.jobs.get_by_id(job_id)
        return deleted_job, 204

    def post(self, job_id):
        '''
        Method to patch job info
        '''
        simulation_root = ''

        manager = JIM(request, simulation_root=simulation_root)

        manager.patch_and_transfer()
        manager.transfer_scripts()
        manager.run_remote_scripts()

        # TODO add an actual check on "success"
        result = {"success": "true", "message": "patch applied"}
        return result, 201


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
        # Require valid Job JSON
        if not is_valid_job_json(job):
            abort(400, message="Message body is not valid Job JSON")
        job_id = job.get("id")
        if self.jobs.exists(job_id):
            abort(409, message="Job with ID {} already "
                               "exists".format(job_id))
        else:
            job = self.jobs.create(job)
            return job, 200, {'Content-Type': 'application/json'}

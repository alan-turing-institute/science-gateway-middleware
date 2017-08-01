import json_merge_patch
from flask_restful import Resource, abort, request
from middleware.job.model import is_valid_job_json, job_summary_json
from middleware.job_information_manager import job_information_manager as JIM
import os


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

    def patch(self, job_id):
        # Require Job to exist in order to amend it
        job_old = self.jobs.get_by_id(job_id)
        if job_old is None:
            self.abort_if_not_found(job_id)
        # Get Job JSON if present
        job_partial = request.json
        if job_partial is None:
            abort(400, message="Message body could not be parsed as JSON")
        # Check job_id route parameter consistent with id in JSON data (if
        # provided).
        # NOTE: For patches it is ok for ID not to exist in the JSON
        job_id_json = job_partial.get("id")
        if job_id_json is not None and job_id != job_id_json:
            abort(409, message="Job ID in URL ({}) does not match job "
                               "ID in message JSON ({}).".format(job_id,
                                                                 job_id_json))
        # Try and patch Job
        job_new = json_merge_patch.merge(job_old, job_partial)
        # Require patched Job to be valid
        if not is_valid_job_json(job_new):
            abort(400, message="Applying patch results in invalid Job JSON")
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
        Submit/run the job using current parameters data in the database
        '''
        simulation_root = ''  # this needs to be stored in job data structure
        job, response, content_type = self.get(job_id)

        manager = JIM(job, simulation_root=simulation_root)

        manager.patch_and_transfer()
        manager.transfer_scripts()
        out, err, exit_codes = manager.run_remote_scripts()

        # TODO add an actual check on "success"
        result = {"stdout": out, "stderr": err, "exit_codes": exit_codes}
        return result, 201


class JobsApi(Resource):
    '''API for listing a collection of jobs (GET) and creating a new
    individual job (POST)'''
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def get(self):
        def list_job_summary_json(job_id):
            job = self.jobs.get_by_id(job_id)
            summary_json = job_summary_json(job)
            summary_json["uri"] = "/job/{}".format(job_id)
            return summary_json
        job_ids = self.jobs.list_ids()
        summary_list = [list_job_summary_json(job_id) for job_id in job_ids]
        return summary_list, 200, {'Content-Type': 'application/json'}

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


class actionHandler():
    '''
    Class to abstract the the identification and execution of the action api.
    '''
    def run_verb(self, job, verb):
        '''
        Given a verb as a string (eg 'RUN' or 'CANCEL') and a job, execute the
        script on the remote server
        '''

        manager = JIM(job, simulation_root='')
        remote_path, remote_script = manager.get_action_script(verb)

        # Ensure we have a script to run before trying to run it
        if remote_script:
            a, b, c = manager._run_remote_script(remote_script, remote_path)
            result = {"stdout": a, "stderr": b, "exit_code": c}
            return result, 200
        else:
            return abort(400, message="{} script not found".format(verb))


class SETUPApi(Resource):
    '''API endpoint called to setup a job on the cluster (POST)'''
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def post(self, job_id):

        job = self.jobs.get_by_id(job_id)
        handler = actionHandler()

        return handler.run_verb(job, 'SETUP')


class PROGRESSApi(Resource):
    '''API endpoint called to check the progress a job on the cluster (POST)'''
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def post(self, job_id):

        job = self.jobs.get_by_id(job_id)
        handler = actionHandler()

        return handler.run_verb(job, 'PROGRESS')


class CANCELApi(Resource):
    '''API endpoint called to cancel a job on the cluster (POST)'''
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def post(self, job_id):

        job = self.jobs.get_by_id(job_id)
        handler = actionHandler()

        return handler.run_verb(job, 'CANCEL')


class RUNApi(Resource):
    '''API endpoint called to run a job on the cluster (POST)'''
    def __init__(self, **kwargs):
        # Inject job service
        self.jobs = kwargs['job_repository']

    def post(self, job_id):

        job = self.jobs.get_by_id(job_id)
        handler = actionHandler()

        return handler.run_verb(job, 'RUN')

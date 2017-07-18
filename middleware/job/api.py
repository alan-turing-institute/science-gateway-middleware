from flask_restful import Resource, abort, request
from flask import jsonify, request
from os import makedirs
import os
from os.path import dirname, basename
from middleware.job.model import is_valid_job_json
from middleware.patcher import (apply_patch, patch_and_transfer_template_files,
                                transfer_files, run_remote_script)


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
        simulation_root = '/home/vm-admin/simulation'

        # TODO build data structure here with full remote path information, so
        # generating full paths is a once only operation
        input_data = {
            'id': request.json['id'],
            'templates': request.json['templates'],
            'parameters': request.json['parameters'],
            'scripts': request.json['scripts']
        }

        template_list = input_data["templates"]
        script_list = input_data["scripts"]
        parameter_patch = input_data["parameters"]

        #patch_and_transfer_template_files(template_list, parameter_patch)
        #transfer_files(script_list)

        for script in script_list:
            script_name = basename(script["source_uri"])
            remote_location = os.path.join(simulation_root,
                                           script["destination_path"])
            #run_remote_script(script_name, remote_location)

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

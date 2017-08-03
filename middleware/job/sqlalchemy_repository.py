from middleware.core import db
from middleware.job.db_models import (
    Job,
    Parameter,
    Template,
    Input,
    Script
)
from middleware.job.db_schema import (
    JobSchema,
    ParameterSchema,
    TemplateSchema,
    InputSchema,
    ScriptSchema
)


class JobRepositorySqlAlchemy():
    '''Job service backed by an SQLAlchemy provided database.'''

    def __init__(self):
        pass

    def exists(self, job_id):
        exists_boolean = db.session.query(
            db.exists().where(Job.id == job_id)
        ).scalar()
        return exists_boolean

    def create(self, job):
        job_id = job.get("id")
        if not self.exists(job_id):
            # Add job if it is not already in job list
            db_content, errors = JobSchema().load(job)
            db.session.add(db_content)
            db.session.commit()
            return self.get_by_id(job_id)
        else:
            return None

    def get_by_id(self, job_id):
        if self.exists(job_id):
            job_object = Job.query.filter_by(id=job_id).first()
            job_json = JobSchema().dump(job_object).data
            return job_json
        else:
            return None

    def update(self, job):
        job_id = job.get("id")
        # if self.exists(job_id):

            # TODO implement SQLAlchemy update procedure

        return None

        #     return self.get_by_id(job_id)
        # else:
        #     return None

    def delete(self, job_id):
        if self.exists(job_id):
            # If job exists, remove job from dictionary and return removed job
            Job.query.filter_by(id=job_id).delete()
            db.session.commit()
            return None
        else:
            return None

    # def list_ids(self):
    #     return [key for key, val in self._jobs.items()]

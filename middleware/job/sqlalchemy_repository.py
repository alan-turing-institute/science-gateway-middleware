from middleware.job.models import (
    Job,
    Parameter,
    Template,
    Input,
    Script
)
from middleware.job.schema import (
    JobSchema,
    ParameterSchema,
    TemplateSchema,
    InputSchema,
    ScriptSchema
)


class JobRepositorySqlAlchemy():
    '''Job service backed by an SQLAlchemy provided database.'''

    def __init__(self, session):
        self._session = session
        pass

    def exists(self, job_id):
        count = self._session.query(Job.id).filter_by(id=job_id).count()
        return count > 0

    def create(self, job):
        job_id = job.id
        if not self.exists(job_id):
            # Add job if it is not already in job list
            self._session.add(job)
            self._session.commit()
            return self.get_by_id(job_id)
        else:
            return None

    def get_by_id(self, job_id):
        return Job.query.filter_by(id=job_id).first()

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
            self._session.commit()
            return None
        else:
            return None

    # def list_ids(self):
    #     return [key for key, val in self._jobs.items()]

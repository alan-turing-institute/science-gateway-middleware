from middleware.job.models import Job


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
        return self._session.query(Job).filter_by(id=job_id).first()

    def update(self, job):
        job_id = job.id
        if self.exists(job_id):
            self._session.merge(job)
        # Return result of querying repo for Job. This will be None if the Job
        # did not already exist in the repo and the updated Job if it did
        return self.get_by_id(job_id)

    def delete(self, job_id):
        if self.exists(job_id):
            # If job exists, remove job from dictionary and return removed job
            self._session.query(Job).filter_by(id=job_id).delete()
            self._session.commit()
            return None
        else:
            return None

    def list_ids(self):
        # For some reason, we get a listof tuples back with empty second
        # elements when we put Job.id in the query
        return [id[0] for id in self._session.query(Job.id)]

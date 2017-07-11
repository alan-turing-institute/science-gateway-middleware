

class JobRepositoryMemory():
    '''Job service backed by an in-memory array for job storage. Used for
    testing'''
    def __init__(self):
        self._jobs = {}

    def exists(self, job_id):
        return (job_id in self._jobs)

    def create(self, job):
        job_id = job["id"]
        if(not self.exists(job_id)):
            # Add job if it is not already in job list
            self._jobs[job_id] = job
            return self.get_by_id(job_id)
        else:
            return None

    def get_by_id(self, job_id):
        # Note: We could skip the whole if..else check for the existence of
        # job_id as a key as the dictionary.get() method returns None if the
        # key does not exist.
        if(self.exists(job_id)):
            return self._jobs.get(job_id)
        else:
            return None

    def update(self, job):
        job_id = job["id"]
        if(self.exists(job_id)):
            # Replace job if already in job list
            self._jobs[job_id] = job
            return self.get_by_id(job_id)
        else:
            return None

    def delete(self, job):
        job_id = job["id"]
        if(self.exists(job_id)):
            # If job exists, remove job from dictionary and return removed job
            return self._jobs.pop(job_id)
        else:
            return None

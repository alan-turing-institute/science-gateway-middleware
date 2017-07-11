

class JobRepositoryMemory():
    '''Job service backed by an in-memory array for job storage. Used for
    testing'''
    def __init__(self):
        self._jobs = {}

    def create(self, job):
        job_id = job["id"]
        if(job_id not in self._jobs):
            # Add job if it is not already in job list
            self._jobs[job_id] = job
            return job
        else:
            return None

    def get_by_id(self, job_id):
        if(job_id in self._jobs):
            return self._jobs[job_id]
        else:
            return None

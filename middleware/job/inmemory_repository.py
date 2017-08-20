

class JobRepositoryMemory():
    '''Job service backed by an in-memory array for job storage. Used for
    testing'''
    def __init__(self):
        self._jobs = {}

    def exists(self, job_id):
        return (job_id in self._jobs)

    def create(self, job):
        job_id = job.get("id")
        if not self.exists(job_id):
            # Add job if it is not already in job list
            self._jobs[job_id] = job
            return self.get_by_id(job_id)
        else:
            return None

    def get_by_id(self, job_id):
        if self.exists(job_id):
            return self._jobs.get(job_id)
        else:
            return None

    def update(self, job):
        job_id = job.get("id")
        if self.exists(job_id):
            # Replace job if already in job list
            self._jobs[job_id] = job
            return self.get_by_id(job_id)
        else:
            return None

    def delete(self, job_id):
        if self.exists(job_id):
            # If job exists, remove job from dictionary and return removed job
            self._jobs.pop(job_id)
            return None
        else:
            return None

    def list_ids(self):
        return [key for key, val in self._jobs.items()]


class CaseRepositoryMemory():
    '''Case service backed by an in-memory array for case storage. Used for
    testing'''
    def __init__(self):
        self._cases = {}

    def exists(self, case_id):
        return (case_id in self._cases)

    def create(self, case):
        case_id = case.get("id")
        if not self.exists(case_id):
            # Add case if it is not already in case list
            self._cases[case_id] = case
            return self.get_by_id(case_id)
        else:
            return None

    def get_by_id(self, case_id):
        if self.exists(case_id):
            return self._cases.get(case_id)
        else:
            return None

    def list_ids(self):
        return [key for key, val in self._cases.items()]

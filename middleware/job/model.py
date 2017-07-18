
def is_valid_job_json(job):
    valid = True
    # Must have ID field
    if job.get("id") is None:
        valid = False
    return valid


def job_summary_json(job):
    job_id = job.get("id")
    return {"id": job_id}

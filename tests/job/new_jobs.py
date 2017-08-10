from middleware.job.models import Job, Parameter, Template, Script, Input


def new_job1():
    # NOTE: Ensure to update new_job1_json() to match any changes made here
    job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    job = Job(id=job_id)
    job.user = "j1user"
    job.parameters.append(Parameter(name="j1p1name", value="j1p1value"))
    job.parameters.append(Parameter(name="j1p2name", value="j1p2value"))
    job.templates.append(Template(source_uri="j1t1source",
                                  destination_path="j1t1_dest"))
    job.templates.append(Template(source_uri="j1t2source",
                                  destination_path="j1t2_dest"))
    job.scripts.append(Script(action="j1s1action", source_uri="j1s1source",
                              destination_path="j1s1_dest"))
    job.scripts.append(Script(action="j1s2action", source_uri="j1s2source",
                              destination_path="j1s2_dest"))
    job.inputs.append(Input(source_uri="j1i1source",
                            destination_path="j1i1_dest"))
    job.inputs.append(Input(source_uri="j1i2source",
                            destination_path="j1i2_dest"))
    return job


def new_job1_json():
    # NOTE: Ensure to update new_job1() to match any changes made here
    return {"id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "user": "j1user",
            "parameters": [{"name": "j1p1name", "value": "j1p1value"},
                           {"name": "j1p2name", "value": "j1p2value"}],
            "templates": [{"source_uri": "j1t1source",
                           "destination_path": "j1t1_dest"},
                          {"source_uri": "j1t2source",
                           "destination_path": "j1t2_dest"}],
            "scripts": [{"action": "j1s1action", "source_uri": "j1s1source",
                         "destination_path": "j1s1_dest"},
                        {"action": "j1s2action", "source_uri": "j1s2source",
                         "destination_path": "j1s2_dest"}],
            "inputs": [{"source_uri": "j1i1source",
                        "destination_path": "j1i1_dest"},
                       {"source_uri": "j1i2source",
                        "destination_path": "j1i2_dest"}]}


def new_job2():
    # NOTE: Ensure to update new_job2_json() to match any changes made here
    job_id = "9044394f-de29-4be3-857f-33a4fdca0be3"
    job = Job(id=job_id)
    job.user = "j2user"
    job.parameters.append(Parameter(name="j2p1name", value="j2p1value"))
    job.parameters.append(Parameter(name="j2p2name", value="j2p2value"))
    job.templates.append(Template(source_uri="j2t1source",
                                  destination_path="j2t1_dest"))
    job.templates.append(Template(source_uri="j2t2source",
                                  destination_path="j2t2_dest"))
    job.scripts.append(Script(action="j2s1action", source_uri="j2s1source",
                              destination_path="j2s1_dest"))
    job.scripts.append(Script(action="j2s2action", source_uri="j2s2source",
                              destination_path="j2s2_dest"))
    job.inputs.append(Input(source_uri="j2i1source",
                            destination_path="j2i1_dest"))
    job.inputs.append(Input(source_uri="j2i2source",
                            destination_path="j2i2_dest"))
    return job


def new_job2_json():
    # NOTE: Ensure to update new_job2() to match any changes made here
    return {"id": "9044394f-de29-4be3-857f-33a4fdca0be3",
            "user": "j2user",
            "parameters": [{"name": "j2p1name", "value": "j2p1value"},
                           {"name": "j2p2name", "value": "j2p2value"}],
            "templates": [{"source_uri": "j2t1source",
                           "destination_path": "j2t1_dest"},
                          {"source_uri": "j2t2source",
                           "destination_path": "j2t2_dest"}],
            "scripts": [{"action": "j2s1action", "source_uri": "j2s1source",
                         "destination_path": "j2s1_dest"},
                        {"action": "j2s2action", "source_uri": "j2s2source",
                         "destination_path": "j2s2_dest"}],
            "inputs": [{"source_uri": "j2i1source",
                        "destination_path": "j2i1_dest"},
                       {"source_uri": "j2i2source",
                        "destination_path": "j2i2_dest"}]}


def new_job3():
    job_id = "eadcd354-a433-48ed-bdc7-e3b2457a1918"
    job = Job(id=job_id)
    job.user = "j3user"
    job.parameters.append(Parameter(name="j3p1name", value="j3p1value"))
    job.parameters.append(Parameter(name="j3p2name", value="j3p2value"))
    job.templates.append(Template(source_uri="j3t1source",
                                  destination_path="j3t1_dest"))
    job.templates.append(Template(source_uri="j3t2source",
                                  destination_path="j3t2_dest"))
    job.scripts.append(Script(action="j3s1action", source_uri="j3s1source",
                              destination_path="j3s1_dest"))
    job.scripts.append(Script(action="j3s2action", source_uri="j3s2source",
                              destination_path="j3s2_dest"))
    job.inputs.append(Input(source_uri="j3i1source",
                            destination_path="j3i1_dest"))
    job.inputs.append(Input(source_uri="j3i2source",
                            destination_path="j3i2_dest"))
    return job


def new_job4():
    job_id = "eadcd354-a433-48ed-bdc7-e3b2457a1918"
    job = Job(id=job_id)
    job.user = "j4user"
    job.parameters.append(Parameter(name="j4p1name", value="j4p1value"))
    job.parameters.append(Parameter(name="j4p2name", value="j4p2value"))
    job.templates.append(Template(source_uri="j4t1source",
                                  destination_path="j4t1_dest"))
    job.templates.append(Template(source_uri="j4t2source",
                                  destination_path="j4t2_dest"))
    job.scripts.append(Script(action="RUN", source_uri="j4s1source",
                              destination_path="j3s1_dest"))
    job.scripts.append(Script(action="PROGRESS", source_uri="j4s2source",
                              destination_path="j4s2_dest"))
    job.scripts.append(Script(action="CANCEL", source_uri="j4s3source",
                              destination_path="j4s1_dest"))
    job.scripts.append(Script(action="SETUP", source_uri="j4s4source",
                              destination_path="j4s4_dest"))
    job.inputs.append(Input(source_uri="j4i1source",
                            destination_path="j4i1_dest"))
    job.inputs.append(Input(source_uri="j4i2source",
                            destination_path="j4i2_dest"))
    return job

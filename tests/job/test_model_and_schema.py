from middleware.job.models import Job, Parameter, Template, Script, Input
from middleware.job.schema import job_to_json, json_to_job, JobSchema
from uuid import UUID, uuid4, uuid1


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
    job.scripts.append(Script(command="j1s1command", source_uri="j1s1source",
                              destination_path="j1s1_dest"))
    job.scripts.append(Script(command="j1s2command", source_uri="j1s2source",
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
            "scripts": [{"command": "j1s1command", "source_uri": "j1s1source",
                         "destination_path": "j1s1_dest"},
                        {"command": "j1s2command", "source_uri": "j1s2source",
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
    job.scripts.append(Script(command="j2s1command", source_uri="j2s1source",
                              destination_path="j2s1_dest"))
    job.scripts.append(Script(command="j2s2command", source_uri="j2s2source",
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
            "scripts": [{"command": "j2s1command", "source_uri": "j2s1source",
                         "destination_path": "j2s1_dest"},
                        {"command": "j2s2command", "source_uri": "j2s2source",
                         "destination_path": "j2s2_dest"}],
            "inputs": [{"source_uri": "j2i1source",
                        "destination_path": "j2i1_dest"},
                       {"source_uri": "j2i2source",
                        "destination_path": "j2i2_dest"}]}


class TestModel(object):
    def test_new_job_with_no_id_generates_uuid4_id(self):
        job = Job()
        # ID should be a uuid4 UUID
        assert UUID(job.id).version == 4

    def test_new_job_with_id_sets_id_to_that_provided(self):
        job_id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        job = Job(job_id)
        assert job.id == job_id

    def test_fully_identical_jobs_evaluate_as_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        assert job1 == job2

    def test_full_jobs_differing_only_by_id_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.id = "ad460823-370c-48dd-a09f-a7564bb458f1"
        assert job1 != job2

    def test_full_jobs_differing_only_by_user_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.user = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_param_name_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.parameters[0].name = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_param_value_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.parameters[0].value = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_param_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.parameters[0]
        job2.parameters[0] = job2.parameters[1]
        job2.parameters[1] = temp
        assert job2.parameters[1] == job1.parameters[0]
        assert job2.parameters[0] == job1.parameters[1]
        assert job1 == job2

    def test_full_jobs_differing_only_by_template_source_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.templates[0].source_uri = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_template_dest_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.templates[0].destination_path = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_template_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.templates[0]
        job2.templates[0] = job2.templates[1]
        job2.templates[1] = temp
        assert job2.templates[1] == job1.templates[0]
        assert job2.templates[0] == job1.templates[1]
        assert job1 == job2

    def test_full_jobs_differing_only_by_script_command_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.scripts[0].command = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_script_source_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.scripts[0].source_uri = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_script_dest_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.scripts[0].destination_path = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_script_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.scripts[0]
        job2.scripts[0] = job2.scripts[1]
        job2.scripts[1] = temp
        assert job2.scripts[1] == job1.scripts[0]
        assert job2.scripts[0] == job1.scripts[1]
        assert job1 == job2

    def test_full_jobs_differing_only_by_input_source_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.inputs[0].source_uri = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_input_dest_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.inputs[0].destination_path = "changed"
        assert job1 != job2

    def test_full_jobs_differing_only_by_swapped_input_order_equal(self):
        # Ordering of parameters should not matter for equivalence
        job1 = new_job1()
        job2 = new_job1()
        temp = job2.inputs[0]
        job2.inputs[0] = job2.inputs[1]
        job2.inputs[1] = temp
        assert job2.inputs[1] == job1.inputs[0]
        assert job2.inputs[0] == job1.inputs[1]
        assert job1 == job2

    def test_job_make_object(self):
        job1_json = new_job1_json()
        expected_job1 = new_job1()
        job1 = JobSchema().make_job(job1_json)
        assert job1 == expected_job1

    def test_json_to_job(self):
        job1_json = new_job1_json()
        expected_job1 = new_job1()
        job1 = json_to_job(job1_json)
        assert job1 == expected_job1

    def test_job_to_json(self):
        job1 = new_job1()
        job1_json = job_to_json(job1)
        expected_job1_json = new_job1_json()
        assert job1_json == expected_job1_json
        job2 = new_job2()
        job2_json = job_to_json(job2)
        expected_job2_json = new_job2_json()
        assert job2_json == expected_job2_json

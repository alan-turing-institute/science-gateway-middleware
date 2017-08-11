from middleware.job.models import Job
from middleware.job.schema import job_to_json, json_to_job, JobSchema
from uuid import UUID, uuid4, uuid1

from new_jobs import new_job1, new_job1_json, new_job2, new_job2_json


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

    def test_full_jobs_differing_only_by_script_action_not_equal(self):
        job1 = new_job1()
        job2 = new_job1()
        job2.scripts[0].action = "changed"
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


class TestSchema(object):
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

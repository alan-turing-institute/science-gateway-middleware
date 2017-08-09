from middleware.database import ma
from middleware.job.models import (
    Job,
    Parameter,
    Template,
    Input,
    Script
)


class ParameterSchema(ma.ModelSchema):
    class Meta:
        model = Parameter
        fields = ('name', 'value')


class TemplateSchema(ma.ModelSchema):
    class Meta:
        model = Template
        fields = ('source_uri', 'destination_path')


class ScriptSchema(ma.ModelSchema):
    class Meta:
        model = Script
        fields = ('command', 'source_uri', 'destination_path')


class InputSchema(ma.ModelSchema):
    class Meta:
        model = Input
        fields = ('source_uri', 'destination_path')


class JobSchema(ma.ModelSchema):
    class Meta:
        model = Job
        fields = ('id', 'user', 'parameters', 'templates', 'scripts', 'inputs')

    parameters = ma.List(ma.Nested(ParameterSchema))
    templates = ma.List(ma.Nested(TemplateSchema))
    scripts = ma.List(ma.Nested(ScriptSchema))
    inputs = ma.List(ma.Nested(InputSchema))

    def make_job(self, data):
        assert 'id' in data, "Must specify Job ID"
        parameters = ParameterSchema(many=True)\
            .load(data.get("parameters")).data
        templates = TemplateSchema(many=True).load(data.get("templates")).data
        scripts = ScriptSchema(many=True).load(data.get("scripts")).data
        inputs = InputSchema(many=True).load(data.get("inputs")).data
        job = Job(id=data.get("id"), user=data.get("user"),
                  parameters=parameters, templates=templates, scripts=scripts,
                  inputs=inputs)
        return job


def job_to_json(job):
    """"Convert a Job object to json via its associated
    ModelSchema class
    """
    json_dict = JobSchema().dump(job).data
    # Sort lists
    json_dict["parameters"] = sorted(json_dict["parameters"],
                                     key=lambda p: p.get("name"))
    return json_dict


def json_to_job(job_json):
    """"Convert Job json to a Job object via its associated
    ModelSchema class
    """
    job = JobSchema().make_job(job_json)
    return job

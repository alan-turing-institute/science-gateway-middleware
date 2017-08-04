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
        fields = ('name', 'value')


class TemplateSchema(ma.ModelSchema):
    class Meta:
        fields = ('source_uri', 'destination_path')


class ScriptSchema(ma.ModelSchema):
    class Meta:
        fields = ('source_uri', 'destination_path')


class InputSchema(ma.ModelSchema):
    class Meta:
        fields = ('source_uri', 'destination_path')


class JobSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'parameters', 'templates', 'scripts', 'inputs')

    parameters = ma.List(ma.Nested(ParameterSchema))
    templates = ma.List(ma.Nested(TemplateSchema))
    scripts = ma.List(ma.Nested(ScriptSchema))
    inputs = ma.List(ma.Nested(InputSchema))


def job_to_json(job):
    """"Convert a Job object to json via its associated
    ModelSchema class
    """
    print(JobSchema().dump(job).data)
    return JobSchema().dump(job).data

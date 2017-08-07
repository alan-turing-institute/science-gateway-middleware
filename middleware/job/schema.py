from middleware.database import ma
from middleware.database import db

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

    def make_object(self, data):
        print(data)
        return Job(**data)


def job_to_json(job):
    """"Convert a Job object to json via its associated
    ModelSchema class
    """
    return JobSchema().dump(job).data

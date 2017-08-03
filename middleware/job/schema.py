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


class TemplateSchema(ma.ModelSchema):
    class Meta:
        model = Template


class ScriptSchema(ma.ModelSchema):
    class Meta:
        model = Script


class InputSchema(ma.ModelSchema):
    class Meta:
        model = Input


class JobSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'parameters', 'templates', 'scripts', 'inputs')

    parameters = ma.List(ma.Nested(ParameterSchema))
    templates = ma.List(ma.Nested(TemplateSchema))
    scripts = ma.List(ma.Nested(ScriptSchema))
    inputs = ma.List(ma.Nested(InputSchema))

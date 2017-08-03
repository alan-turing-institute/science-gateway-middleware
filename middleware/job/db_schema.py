from flask_marshmallow.sqla import ModelSchema
from marshmallow import fields

from middleware.job.db_models import (
    Job,
    Parameter,
    Template,
    Input,
    Script
)


class ParameterSchema(ModelSchema):
    class Meta:
        model = Parameter


class TemplateSchema(ModelSchema):
    class Meta:
        model = Template


class ScriptSchema(ModelSchema):
    class Meta:
        model = Script


class InputSchema(ModelSchema):
    class Meta:
        model = Input


class JobSchema(ModelSchema):
    class Meta:
        fields = ('id', 'parameters', 'templates', 'scripts', 'inputs')

    parameters = fields.List(fields.Nested(ParameterSchema))
    templates = fields.List(fields.Nested(TemplateSchema))
    scripts = fields.List(fields.Nested(ScriptSchema))
    inputs = fields.List(fields.Nested(InputSchema))

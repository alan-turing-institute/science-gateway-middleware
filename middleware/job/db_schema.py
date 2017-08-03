from marshmallow import Schema, fields, post_load

from middleware.job.db_models import (
    Job,
    Parameter,
    Template,
    Input,
    Script
)

class ParameterSchema(Schema):
    name = fields.String()
    value = fields.String()
    @post_load
    def make_object(self, data):
        return Parameter(**data)


class TemplateSchema(Schema):
    source_uri = fields.String()
    destination_path = fields.String()
    @post_load
    def make_object(self, data):
        return Template(**data)


class ScriptSchema(Schema):
    source_uri = fields.String()
    destination_path = fields.String()
    @post_load
    def make_object(self, data):
        return Script(**data)


class InputSchema(Schema):
    source_uri = fields.String()
    destination_path = fields.String()
    @post_load
    def make_object(self, data):
        return Input(**data)


class JobSchema(Schema):
    id = fields.String()
    user = fields.String()
    parameters = fields.List(fields.Nested(ParameterSchema))
    templates = fields.List(fields.Nested(TemplateSchema))
    scripts = fields.List(fields.Nested(ScriptSchema))
    inputs = fields.List(fields.Nested(InputSchema))

    @post_load
    def make_object(self, data):

        job_object = Job(id=data['id'])

        if "user" in data:
            job_object.user = data["user"]

        if "parameters" in data:
            job_object.parameters = data["parameters"]

        if "templates" in data:
            job_object.templates = data["templates"]

        if "scripts" in data:
            print(data["scripts"])
            job_object.scripts = data["scripts"]

        if "inputs" in data:
            job_object.inputs = data["inputs"]

        return job_object

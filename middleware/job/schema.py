from middleware.database import ma
from middleware.job.models import (
    Job,
    Family,
    Parameter,
    Template,
    Input,
    Script,
    Case
)
import arrow


class ParameterSchema(ma.ModelSchema):
    class Meta:
        model = Parameter
        fields = ('help',
                  'label',
                  'max_value',
                  'min_value',
                  'name',
                  'type',
                  'type_value',
                  'units',
                  'value',
                  )


class FamilySchema(ma.ModelSchema):
    class Meta:
        model = Family
        fields = ('collapse', 'label', 'name', 'parameters')

    parameters = ma.List(ma.Nested(ParameterSchema))


class TemplateSchema(ma.ModelSchema):
    class Meta:
        model = Template
        fields = ('source_uri', 'destination_path')


class ScriptSchema(ma.ModelSchema):
    class Meta:
        model = Script
        fields = ('action', 'source_uri', 'destination_path')


class InputSchema(ma.ModelSchema):
    class Meta:
        model = Input
        fields = ('source_uri', 'destination_path')


class CaseSchema(ma.ModelSchema):
    class Meta:
        model = Case
        fields = ('id', 'uri', 'label', 'thumbnail', 'description')


class JobSchema(ma.ModelSchema):
    class Meta:
        model = Job
        fields = ('id',
                  'description',
                  'name',
                  'status',
                  'user',
                  'creation_datetime',
                  'start_datetime',
                  'end_datetime',
                  'families',
                  'templates',
                  'scripts',
                  'inputs',
                  'case'
                  )

    families = ma.List(ma.Nested(FamilySchema))
    templates = ma.List(ma.Nested(TemplateSchema))
    scripts = ma.List(ma.Nested(ScriptSchema))
    inputs = ma.List(ma.Nested(InputSchema))
    case = ma.Nested(CaseSchema)

    def make_job(self, data):
        assert 'id' in data, "Must specify Job ID"
        families = FamilySchema(many=True)\
            .load(data.get("families")).data
        templates = TemplateSchema(many=True).load(data.get("templates")).data
        scripts = ScriptSchema(many=True).load(data.get("scripts")).data
        inputs = InputSchema(many=True).load(data.get("inputs")).data

        # TODO load from Cases database once implemented
        case_data = data.get("case")
        case_id = case_data.get("id")
        case_uri = case_data.get("uri")
        case_label = case_data.get("label")
        case_thumbnail = case_data.get("thumbnail")
        case_description = case_data.get("description")
        case = Case(
            id=case_id,
            uri=case_uri,
            label=case_label,
            thumbnail=case_thumbnail,
            description=case_description,
        )

        creation_datetime = arrow.get(
            data.get("creation_datetime"))

        start_datetime = arrow.get(
            data.get("start_datetime"))
        end_datetime = arrow.get(
            data.get("end_datetime"))

        job = Job(
            id=data.get("id"),
            description=data.get("description"),
            name=data.get("name"),
            status=data.get("status"),
            user=data.get("user"),
            creation_datetime=creation_datetime,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            families=families,
            templates=templates,
            scripts=scripts,
            inputs=inputs,
            case=case)
        return job


def job_to_json(job):
    """"Convert a Job object to json via its associated
    ModelSchema class
    """
    json_dict = JobSchema().dump(job).data
    # Sort lists
    # json_dict["families"] = sorted(json_dict["families"],
    #                                key=lambda p: p.get("name"))
    return json_dict


def json_to_job(job_json):
    """"Convert Job json to a Job object via its associated
    ModelSchema class
    """
    job = JobSchema().make_job(job_json)
    return job

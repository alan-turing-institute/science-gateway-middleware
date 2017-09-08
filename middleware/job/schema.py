from middleware.database import ma
from middleware.job.models import (
    Case,
    Job, JobTemplate,
    Family, FamilyTemplate,
    Parameter, ParameterTemplate,
    Template, TemplateTemplate,
    Input, InputTemplate,
    Script, ScriptTemplate,
    CaseSummary
)
import arrow


class CaseSchema(ma.ModelSchema):
    class Meta:
        model = Case
        fields = ('id', 'uri', 'label', 'thumbnail', 'description', 'job')
    job = ma.Nested('JobTemplateSchema')

    def make_case(self, data):
        job_template = JobTemplateSchema().load(data.get("job")).data

        # case uuid used for "id" field is
        # hardcoded in cases json
        case = Case(
            id=data.get("id"),
            uri=data.get("uri"),
            label=data.get("label"),
            thumbnail=data.get("thumbnail"),
            description=data.get("description"),
            job=job_template)
        return case


class JobTemplateSchema(ma.ModelSchema):
    class Meta:
        model = JobTemplate
        fields = ('description',
                  'name',
                  'families',
                  'templates',
                  'scripts',
                  'inputs',
                  )

    families = ma.List(ma.Nested('FamilyTemplateSchema'))
    templates = ma.List(ma.Nested('TemplateTemplateSchema'))
    scripts = ma.List(ma.Nested('ScriptTemplateSchema'))
    inputs = ma.List(ma.Nested('InputTemplateSchema'))
    case = ma.Nested('CaseSchema')

    def make_job_template(self, data):
        families = \
            FamilyTemplateSchema(many=True).load(data.get("families")).data
        templates = \
            TemplateTemplateSchema(many=True).load(data.get("templates")).data
        scripts = \
            ScriptTemplateSchema(many=True).load(data.get("scripts")).data
        inputs = \
            InputTemplateSchema(many=True).load(data.get("inputs")).data

        job_template = JobTemplate(
            description=data.get("description"),
            name=data.get("name"),
            families=families,
            templates=templates,
            scripts=scripts,
            inputs=inputs)
        return job_template


class JobSchema(ma.ModelSchema):
    class Meta:
        model = Job
        fields = ('id',
                  'backend_identifier',
                  'description',
                  'name',
                  'status',
                  'uri',
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

    families = ma.List(ma.Nested('FamilySchema'))
    templates = ma.List(ma.Nested('TemplateSchema'))
    scripts = ma.List(ma.Nested('ScriptSchema'))
    inputs = ma.List(ma.Nested('InputSchema'))
    case = ma.Nested('CaseSummarySchema')

    def make_job(self, data):
        assert 'id' in data, "Must specify Job ID"
        families = FamilySchema(many=True)\
            .load(data.get("families")).data
        templates = TemplateSchema(many=True).load(data.get("templates")).data
        scripts = ScriptSchema(many=True).load(data.get("scripts")).data
        inputs = InputSchema(many=True).load(data.get("inputs")).data

        case = CaseSummarySchema().load(data.get("case")).data

        # Note, `arrow.get(None)` returns present utc time
        # rather than `None`
        data_creation_datetime = data.get("creation_datetime")
        if data_creation_datetime:
            creation_datetime = arrow.get(data.get("creation_datetime"))
        else:
            creation_datetime = None

        data_start_datetime = data.get("start_datetime")
        if data_start_datetime:
            start_datetime = arrow.get(data.get("start_datetime"))
        else:
            start_datetime = None

        data_end_datetime = data.get("end_datetime")
        if data_end_datetime:
            end_datetime = arrow.get(data.get("end_datetime"))
        else:
            end_datetime = None

        job = Job(
            id=data.get("id"),
            backend_identifier=data.get("backend_identifier"),
            description=data.get("description"),
            name=data.get("name"),
            status=data.get("status"),
            uri=data.get("uri"),
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


class JobSummarySchema(ma.ModelSchema):
    class Meta:
        model = Job
        fields = ('id',
                  'uri',
                  'description',
                  'name',
                  'status',
                  'creation_datetime',
                  'start_datetime',
                  'end_datetime',
                  'case'
                  )
    case = ma.Nested('CaseSummarySchema')


class FamilyTemplateSchema(ma.ModelSchema):
    class Meta:
        model = FamilyTemplate
        fields = ('collapse', 'label', 'name', 'parameters')

    parameters = ma.List(ma.Nested('ParameterTemplateSchema'))


class FamilySchema(ma.ModelSchema):
    class Meta:
        model = Family
        fields = ('collapse', 'label', 'name', 'parameters')

    parameters = ma.List(ma.Nested('ParameterSchema'))


class ParameterTemplateSchema(ma.ModelSchema):
    class Meta:
        model = ParameterTemplate
        fields = ('help',
                  'label',
                  'max_value',
                  'min_value',
                  'step',
                  'name',
                  'type',
                  'type_value',
                  'units',
                  'value',
                  )


class ParameterSchema(ma.ModelSchema):
    class Meta:
        model = Parameter
        fields = ('help',
                  'label',
                  'max_value',
                  'min_value',
                  'step',
                  'name',
                  'type',
                  'type_value',
                  'units',
                  'value',
                  )


class TemplateTemplateSchema(ma.ModelSchema):
    class Meta:
        model = TemplateTemplate
        fields = ('source_uri', 'destination_path')


class TemplateSchema(ma.ModelSchema):
    class Meta:
        model = Template
        fields = ('source_uri', 'destination_path')


class ScriptTemplateSchema(ma.ModelSchema):
    class Meta:
        model = ScriptTemplate
        fields = ('action', 'source_uri', 'destination_path')


class ScriptSchema(ma.ModelSchema):
    class Meta:
        model = Script
        fields = ('action', 'source_uri', 'destination_path')


class InputTemplateSchema(ma.ModelSchema):
    class Meta:
        model = InputTemplate
        fields = ('source_uri', 'destination_path')


class InputSchema(ma.ModelSchema):
    class Meta:
        model = Input
        fields = ('source_uri', 'destination_path')


class CaseSummarySchema(ma.ModelSchema):
    class Meta:
        model = CaseSummary
        fields = ('id', 'uri', 'label', 'thumbnail', 'description')


def job_template_to_json(job_template):
    """"Convert a JobTemplate object to json via its associated
    ModelSchema class
    """
    json_dict = JobTemplateSchema().dump(job_template).data
    # Sort lists
    # json_dict["families"] = sorted(json_dict["families"],
    #                                key=lambda p: p.get("name"))
    return json_dict


def job_to_json(job):
    """"Convert a Job object to json via its associated
    ModelSchema class
    """
    json_dict = JobSchema().dump(job).data
    # Sort lists
    # json_dict["families"] = sorted(json_dict["families"],
    #                                key=lambda p: p.get("name"))
    return json_dict


def job_to_summary_json(job):
    json_dict = JobSummarySchema().dump(job).data
    return json_dict


def json_to_job(job_json):
    """"Convert Job json to a Job object via its associated
    ModelSchema class
    """
    job = JobSchema().make_job(job_json)
    return job


def case_to_json(case):
    """"Convert a Case object to json via its associated
    ModelSchema class
    """
    json_dict = CaseSchema().dump(case).data
    # Sort lists
    # json_dict["families"] = sorted(json_dict["families"],
    #                                key=lambda p: p.get("name"))
    return json_dict


def case_to_summary_json(case):
    json_dict = CaseSummarySchema().dump(case).data
    return json_dict

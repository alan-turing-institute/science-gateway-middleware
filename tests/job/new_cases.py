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

from middleware.job.schema import CaseSchema, JobTemplateSchema, JobSchema
from middleware.job.schema import (
    job_to_json, json_to_job, job_template_to_json)

MIDDLEWARE_URL = "https://science-gateway-middleware.azurewebsites.net"

# "c" denotes creation_datetime
# "s" denotes start_datetime
# "e" denotes end_datetime

j1c_iso_string = "2017-08-12T13:38:18.153+05:00"
j1s_iso_string = "2017-08-12T14:38:18.153+05:00"
j1e_iso_string = "2017-08-12T15:38:18.153+05:00"

j2c_iso_string = "2017-08-12T13:38:18.153+00:00"
j2s_iso_string = "2017-08-12T14:38:18.153+00:00"
j2e_iso_string = "2017-08-12T15:38:18.153+00:00"

j3c_iso_string = "2017-08-12T13:38:18.153+00:00"
j3s_iso_string = "2017-08-12T14:38:18.153+00:00"
j3e_iso_string = "2017-08-12T15:38:18.153+00:00"

j4c_iso_string = "2017-08-12T13:38:18.153+00:00"
j4s_iso_string = "2017-08-12T14:38:18.153+00:00"
j4e_iso_string = "2017-08-12T15:38:18.153+00:00"

j5c_iso_string = "2017-08-12T13:38:18.153+00:00"
j5s_iso_string = "2017-08-12T14:38:18.153+00:00"
j5e_iso_string = "2017-08-12T15:38:18.153+00:00"


def arrow_processing(iso_string):
    arrow_object = arrow.get(iso_string)

    # Avoiding arrow_object.to('UTC').format()
    # use str() builtin instead
    # by default, .format() strips millisecond data
    # by default, .format() strips "T" symbol
    utc_string = str(arrow_object.to('UTC'))
    return arrow_object, utc_string


j1c_arrow, j1c_utc_string = arrow_processing(j1c_iso_string)
j1s_arrow, j1s_utc_string = arrow_processing(j1s_iso_string)
j1e_arrow, j1e_utc_string = arrow_processing(j1e_iso_string)

j2c_arrow, j2c_utc_string = arrow_processing(j2c_iso_string)
j2s_arrow, j2s_utc_string = arrow_processing(j2s_iso_string)
j2e_arrow, j2e_utc_string = arrow_processing(j2e_iso_string)

j3c_arrow, j3c_utc_string = arrow_processing(j3c_iso_string)
j3s_arrow, j3s_utc_string = arrow_processing(j3s_iso_string)
j3e_arrow, j3e_utc_string = arrow_processing(j3e_iso_string)

j4c_arrow, j4c_utc_string = arrow_processing(j4c_iso_string)
j4s_arrow, j4s_utc_string = arrow_processing(j4s_iso_string)
j4e_arrow, j4e_utc_string = arrow_processing(j4e_iso_string)

j5c_arrow, j5c_utc_string = arrow_processing(j5c_iso_string)
j5s_arrow, j5s_utc_string = arrow_processing(j5s_iso_string)
j5e_arrow, j5e_utc_string = arrow_processing(j5e_iso_string)


def new_job_template1():
    job = JobTemplate()

    job.description = "j1description"
    job.name = "j1name"

    job.families.append(
        FamilyTemplate(
            label="j1f1label",
            name="j1f1name",
            collapse=True,
            parameters=[
                ParameterTemplate(
                    help="j1f1p1help",
                    label="j1f1p1label",
                    max_value="j1f1p1max_value",
                    min_value="j1f1p1min_value",
                    name="j1f1p1name",
                    type="j1f1p1type",
                    type_value="j1f1p1type_value",
                    units="j1f1p1units",
                          value="j1f1p1value"),
                ParameterTemplate(
                    help="j1f1p2help",
                    label="j1f1p2label",
                    max_value="j1f1p2max_value",
                    min_value="j1f1p2min_value",
                    name="j1f1p2name",
                    type="j1f1p2type",
                    type_value="j1f1p2type_value",
                    units="j1f1p2units",
                    value="j1f1p2value")]
        )
    )

    job.templates.append(TemplateTemplate(
        source_uri="j1t1source",
        destination_path="j1t1_dest"
    ))
    job.templates.append(TemplateTemplate(
        source_uri="j1t2source",
        destination_path="j1t2_dest"))
    job.scripts.append(ScriptTemplate(
        action="j1s1action",
        source_uri="j1s1source",
        destination_path="j1s1_dest"
    ))
    job.scripts.append(ScriptTemplate(
        action="j1s2action",
        source_uri="j1s2source",
        destination_path="j1s2_dest"
    ))
    job.inputs.append(InputTemplate(
        source_uri="j1i1source",
        destination_path="j1i1_dest"
    ))
    job.inputs.append(InputTemplate(
        source_uri="j1i2source",
        destination_path="j1i2_dest"
    ))
    return job



def new_case1():
    case_id = "af7fd241-e816-40e5-9a70-49598a452b7b"
    case = Case(id=case_id)
    case.uri = "{}/api/cases/{}".format(MIDDLEWARE_URL, case_id)
    case.label = "Stirred Tank"
    case.thumbnail = "{}/assets/img/stirred_tank.png".format(MIDDLEWARE_URL)
    case.description = "Here we describe the actual Stirred Tank case."
    case.job = new_job_template1()
    return case





# <codecell> GET api/cases/<case-id>

# fetch case object using <case-id> query
case = new_case1()  # mock
CaseSchema().dump(case).data


from middleware.job.models import case_to_job
job_to_json(case_to_job(case))


# # <codecell>
#
#
# # test a job template
# job_template = new_job_template1()
# JobTemplateSchema().dump(job_template).data
#
# # test a case
# CaseSchema().dump(case).data
#
# # test a job
# job = case_to_job(case)
# JobSchema().dump(job).data

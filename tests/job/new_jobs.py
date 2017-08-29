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

from middleware.job.schema import (
    job_to_json, json_to_job, job_template_to_json)
from config.base import MIDDLEWARE_URL, URI_STEMS

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


def job_uri_string(job_id):
    return "{}{}/{}".format(MIDDLEWARE_URL, URI_STEMS['jobs'], job_id)


def new_job1():
    # NOTE: Ensure to update new_job1_json() to match any changes made here
    job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    job = Job(id=job_id)

    job.uri = job_uri_string(job_id)
    job.description = "j1description"
    job.name = "j1name"
    job.status = "j1status"
    job.user = "j1user"
    job.backend_identifier = "j1backend_identifier"

    # emulate the action of sqlalchemy_utils.ArrowType
    # which converts the supplied arrow object UTC
    # when intantiating a job
    job.creation_datetime = j1c_arrow.to("UTC")
    job.start_datetime = j1s_arrow.to("UTC")
    job.end_datetime = j1e_arrow.to("UTC")

    job.families.append(
        Family(
            label="j1f1label",
            name="j1f1name",
            collapse=True,
            parameters=[
                Parameter(help="j1f1p1help",
                          label="j1f1p1label",
                          max_value="j1f1p1max_value",
                          min_value="j1f1p1min_value",
                          name="j1f1p1name",
                          type="j1f1p1type",
                          type_value="j1f1p1type_value",
                          units="j1f1p1units",
                          value="j1f1p1value"),
                Parameter(help="j1f1p2help",
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

    job.templates.append(Template(
        source_uri="j1t1source",
        destination_path="j1t1_dest"
    ))
    job.templates.append(Template(
        source_uri="j1t2source",
        destination_path="j1t2_dest"
    ))
    job.scripts.append(Script(
        action="j1s1action",
        source_uri="j1s1source",
        destination_path="j1s1_dest"
    ))
    job.scripts.append(Script(
        action="j1s2action",
        source_uri="j1s2source",
        destination_path="j1s2_dest"
    ))
    job.inputs.append(Input(
        source_uri="j1i1source",
        destination_path="j1i1_dest"
    ))
    job.inputs.append(Input(
        source_uri="j1i2source",
        destination_path="j1i2_dest"
    ))
    job.case = CaseSummary(
        id="85b8995c-63a9-474f-8fdc-52c7582ec2ac",
        uri="c1uri",
        label="c1label",
        thumbnail="c1thumbnail",
        description="c1description"
    )
    return job


# input json uses local time
def new_job1_input_json():
    # NOTE: Ensure to update new_job1() to match any changes made here
    uri_string = job_uri_string("d769843b-6f37-4939-96c7-c382c3e74b46")
    return {"id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "uri": uri_string,
            "description": "j1description",
            "name": "j1name",
            "status": "j1status",
            "user": "j1user",
            "backend_identifier": "j1backend_identifier",
            "creation_datetime": j1c_iso_string,
            "start_datetime": j1s_iso_string,
            "end_datetime": j1e_iso_string,
            "families": [
                {
                    "label": "j1f1label",
                    "name": "j1f1name",
                    "collapse": True,
                    "parameters": [
                        {
                            "help": "j1f1p1help",
                            "label": "j1f1p1label",
                            "max_value": "j1f1p1max_value",
                            "min_value": "j1f1p1min_value",
                            "name": "j1f1p1name",
                            "type": "j1f1p1type",
                            "type_value": "j1f1p1type_value",
                            "units": "j1f1p1units",
                            "value": "j1f1p1value"
                        },
                        {
                            "help": "j1f1p2help",
                            "label": "j1f1p2label",
                            "max_value": "j1f1p2max_value",
                            "min_value": "j1f1p2min_value",
                            "name": "j1f1p2name",
                            "type": "j1f1p2type",
                            "type_value": "j1f1p2type_value",
                            "units": "j1f1p2units",
                            "value": "j1f1p2value"
                        }
                    ]
                }
            ],
            "templates": [{"source_uri": "j1t1source",
                           "destination_path": "j1t1_dest"},
                          {"source_uri": "j1t2source",
                           "destination_path": "j1t2_dest"}],
            "scripts": [{"action": "j1s1action", "source_uri": "j1s1source",
                         "destination_path": "j1s1_dest"},
                        {"action": "j1s2action", "source_uri": "j1s2source",
                         "destination_path": "j1s2_dest"}],
            "inputs": [{"source_uri": "j1i1source",
                        "destination_path": "j1i1_dest"},
                       {"source_uri": "j1i2source",
                        "destination_path": "j1i2_dest"}],
            "case": {"id": "85b8995c-63a9-474f-8fdc-52c7582ec2ac",
                     "uri": "c1uri",
                     "label": "c1label",
                     "thumbnail": "c1thumbnail",
                     "description": "c1description"
                     }
            }


# output json uses UTC time
def new_job1_output_json():
    # NOTE: Ensure to update new_job1() to match any changes made here
    uri_string = job_uri_string("d769843b-6f37-4939-96c7-c382c3e74b46")
    return {"id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "uri": uri_string,
            "description": "j1description",
            "name": "j1name",
            "status": "j1status",
            "user": "j1user",
            "backend_identifier": "j1backend_identifier",
            "creation_datetime": j1c_utc_string,
            "start_datetime": j1s_utc_string,
            "end_datetime": j1e_utc_string,
            "families": [
                {
                    "label": "j1f1label",
                    "name": "j1f1name",
                    "collapse": True,
                    "parameters": [
                        {
                            "help": "j1f1p1help",
                            "label": "j1f1p1label",
                            "max_value": "j1f1p1max_value",
                            "min_value": "j1f1p1min_value",
                            "name": "j1f1p1name",
                            "type": "j1f1p1type",
                            "type_value": "j1f1p1type_value",
                            "units": "j1f1p1units",
                            "value": "j1f1p1value"
                        },
                        {
                            "help": "j1f1p2help",
                            "label": "j1f1p2label",
                            "max_value": "j1f1p2max_value",
                            "min_value": "j1f1p2min_value",
                            "name": "j1f1p2name",
                            "type": "j1f1p2type",
                            "type_value": "j1f1p2type_value",
                            "units": "j1f1p2units",
                            "value": "j1f1p2value"
                        }
                    ]
                }
            ],
            "templates": [{"source_uri": "j1t1source",
                           "destination_path": "j1t1_dest"},
                          {"source_uri": "j1t2source",
                           "destination_path": "j1t2_dest"}],
            "scripts": [{"action": "j1s1action", "source_uri": "j1s1source",
                         "destination_path": "j1s1_dest"},
                        {"action": "j1s2action", "source_uri": "j1s2source",
                         "destination_path": "j1s2_dest"}],
            "inputs": [{"source_uri": "j1i1source",
                        "destination_path": "j1i1_dest"},
                       {"source_uri": "j1i2source",
                        "destination_path": "j1i2_dest"}],
            "case": {"id": "85b8995c-63a9-474f-8fdc-52c7582ec2ac",
                     "uri": "c1uri",
                     "label": "c1label",
                     "thumbnail": "c1thumbnail",
                     "description": "c1description"
                     }
            }


def new_job2():
    # NOTE: Ensure to update new_job2_json() to match any changes made here
    job_id = "9044394f-de29-4be3-857f-33a4fdca0be3"
    job = Job(id=job_id)

    job.uri = job_uri_string(job_id)
    job.description = "j2description"
    job.name = "j2name"
    job.status = "j2status"
    job.user = "j2user"
    job.backend_identifier = "j2backend_identifier"

    # emulate the action of sqlalchemy_utils.ArrowType
    # which converts the supplied arrow object UTC
    # when intantiating a job
    job.creation_datetime = j2c_arrow.to("UTC")
    job.start_datetime = j2s_arrow.to("UTC")
    job.end_datetime = j2e_arrow.to("UTC")

    job.families.append(
        Family(
            label="j2f1label",
            name="j2f1name",
            collapse=True,
            parameters=[
                Parameter(help="j2f1p1help",
                          label="j2f1p1label",
                          max_value="j2f1p1max_value",
                          min_value="j2f1p1min_value",
                          name="j2f1p1name",
                          type="j2f1p1type",
                          type_value="j2f1p1type_value",
                          units="j2f1p1units",
                          value="j2f1p1value"),
                Parameter(help="j2f1p2help",
                          label="j2f1p2label",
                          max_value="j2f1p2max_value",
                          min_value="j2f1p2min_value",
                          name="j2f1p2name",
                          type="j2f1p2type",
                          type_value="j2f1p2type_value",
                          units="j2f1p2units",
                          value="j2f1p2value")]
        )
    )

    job.templates.append(Template(
        source_uri="j2t1source",
        destination_path="j2t1_dest"
    ))
    job.templates.append(Template(
        source_uri="j2t2source",
        destination_path="j2t2_dest"
    ))
    job.scripts.append(Script(
        action="j2s1action",
        source_uri="j2s1source",
        destination_path="j2s1_dest"
    ))
    job.scripts.append(Script(
        action="j2s2action",
        source_uri="j2s2source",
        destination_path="j2s2_dest"
    ))
    job.inputs.append(Input(
        source_uri="j2i1source",
        destination_path="j2i1_dest"
    ))
    job.inputs.append(Input(
        source_uri="j2i2source",
        destination_path="j2i2_dest"
    ))
    job.case = CaseSummary(
        id="85b8995c-63a9-474f-8fdc-52c7582ec2ac",
        uri="c1uri",
        label="c1label",
        thumbnail="c1thumbnail",
        description="c1description"
    )
    return job


def new_job2_input_json():
    # NOTE: Ensure to update new_job2() to match any changes made here
    uri_string = job_uri_string("9044394f-de29-4be3-857f-33a4fdca0be3")
    return {"id": "9044394f-de29-4be3-857f-33a4fdca0be3",
            "uri": uri_string,
            "description": "j2description",
            "name": "j2name",
            "status": "j2status",
            "user": "j2user",
            "backend_identifier": "j2backend_identifier",
            "creation_datetime": j2c_iso_string,
            "start_datetime": j2s_iso_string,
            "end_datetime": j2e_iso_string,
            "families": [
                {
                    "label": "j2f1label",
                    "name": "j2f1name",
                    "collapse": True,
                    "parameters": [
                        {
                            "help": "j2f1p1help",
                            "label": "j2f1p1label",
                            "max_value": "j2f1p1max_value",
                            "min_value": "j2f1p1min_value",
                            "name": "j2f1p1name",
                            "type": "j2f1p1type",
                            "type_value": "j2f1p1type_value",
                            "units": "j2f1p1units",
                            "value": "j2f1p1value"
                        },
                        {
                            "help": "j2f1p2help",
                            "label": "j2f1p2label",
                            "max_value": "j2f1p2max_value",
                            "min_value": "j2f1p2min_value",
                            "name": "j2f1p2name",
                            "type": "j2f1p2type",
                            "type_value": "j2f1p2type_value",
                            "units": "j2f1p2units",
                            "value": "j2f1p2value"
                        }
                    ]
                }
            ],
            "templates": [{"source_uri": "j2t1source",
                           "destination_path": "j2t1_dest"},
                          {"source_uri": "j2t2source",
                           "destination_path": "j2t2_dest"}],
            "scripts": [{"action": "j2s1action", "source_uri": "j2s1source",
                         "destination_path": "j2s1_dest"},
                        {"action": "j2s2action", "source_uri": "j2s2source",
                         "destination_path": "j2s2_dest"}],
            "inputs": [{"source_uri": "j2i1source",
                        "destination_path": "j2i1_dest"},
                       {"source_uri": "j2i2source",
                        "destination_path": "j2i2_dest"}],
            "case": {"id": "85b8995c-63a9-474f-8fdc-52c7582ec2ac",
                     "uri": "j1c1uri",
                     "label": "j1c1label",
                     "thumbnail": "j1c1thumbnail",
                     "description": "j1c1description"
                     }
            }


def new_job2_output_json():
    # NOTE: Ensure to update new_job2() to match any changes made here
    uri_string = job_uri_string("9044394f-de29-4be3-857f-33a4fdca0be3")
    return {"id": "9044394f-de29-4be3-857f-33a4fdca0be3",
            "uri": uri_string,
            "description": "j2description",
            "name": "j2name",
            "status": "j2status",
            "user": "j2user",
            "backend_identifier": "j2backend_identifier",
            "creation_datetime": j2c_utc_string,
            "start_datetime": j2s_utc_string,
            "end_datetime": j2e_utc_string,
            "families": [
                {
                    "label": "j2f1label",
                    "name": "j2f1name",
                    "collapse": True,
                    "parameters": [
                        {
                            "help": "j2f1p1help",
                            "label": "j2f1p1label",
                            "max_value": "j2f1p1max_value",
                            "min_value": "j2f1p1min_value",
                            "name": "j2f1p1name",
                            "type": "j2f1p1type",
                            "type_value": "j2f1p1type_value",
                            "units": "j2f1p1units",
                            "value": "j2f1p1value"
                        },
                        {
                            "help": "j2f1p2help",
                            "label": "j2f1p2label",
                            "max_value": "j2f1p2max_value",
                            "min_value": "j2f1p2min_value",
                            "name": "j2f1p2name",
                            "type": "j2f1p2type",
                            "type_value": "j2f1p2type_value",
                            "units": "j2f1p2units",
                            "value": "j2f1p2value"
                        }
                    ]
                }
            ],
            "templates": [{"source_uri": "j2t1source",
                           "destination_path": "j2t1_dest"},
                          {"source_uri": "j2t2source",
                           "destination_path": "j2t2_dest"}],
            "scripts": [{"action": "j2s1action", "source_uri": "j2s1source",
                         "destination_path": "j2s1_dest"},
                        {"action": "j2s2action", "source_uri": "j2s2source",
                         "destination_path": "j2s2_dest"}],
            "inputs": [{"source_uri": "j2i1source",
                        "destination_path": "j2i1_dest"},
                       {"source_uri": "j2i2source",
                        "destination_path": "j2i2_dest"}],
            "case": {"id": "85b8995c-63a9-474f-8fdc-52c7582ec2ac",
                     "uri": "c1uri",
                     "label": "c1label",
                     "thumbnail": "c1thumbnail",
                     "description": "c1description"
                     }
            }


def new_job3():
    job_id = "eadcd354-a433-48ed-bdc7-e3b2457a1918"
    job = Job(id=job_id)

    job.uri = job_uri_string(job_id)
    job.description = "j3description"
    job.name = "j3name"
    job.status = "j3status"
    job.user = "j3user"
    job.backend_identifier = "j3backend_identifier"

    # emulate the action of sqlalchemy_utils.ArrowType
    # which converts the supplied arrow object UTC
    # when intantiating a job
    job.creation_datetime = j3c_arrow.to("UTC")
    job.start_datetime = j3s_arrow.to("UTC")
    job.end_datetime = j3e_arrow.to("UTC")

    job.families.append(
        Family(
            label="j3f1label",
            name="j3f1name",
            collapse=True,
            parameters=[
                Parameter(help="j3f1p1help",
                          label="j3f1p1label",
                          max_value="j3f1p1max_value",
                          min_value="j3f1p1min_value",
                          name="j3f1p1name",
                          type="j3f1p1type",
                          type_value="j3f1p1type_value",
                          units="j3f1p1units",
                          value="j3f1p1value"),
                Parameter(help="j3f1p2help",
                          label="j3f1p2label",
                          max_value="j3f1p2max_value",
                          min_value="j3f1p2min_value",
                          name="j3f1p2name",
                          type="j3f1p2type",
                          type_value="j3f1p2type_value",
                          units="j3f1p2units",
                          value="j3f1p2value")]
        )
    )

    job.templates.append(Template(
        source_uri="j3t1source",
        destination_path="j3t1_dest"
    ))
    job.templates.append(Template(
        source_uri="j3t2source",
        destination_path="j3t2_dest"
    ))
    job.scripts.append(Script(
        action="j3s1action",
        source_uri="j3s1source",
        destination_path="j3s1_dest"
    ))
    job.scripts.append(Script(
        action="j3s2action",
        source_uri="j3s2source",
        destination_path="j3s2_dest"
    ))
    job.inputs.append(Input(
        source_uri="j3i1source",
        destination_path="j3i1_dest"
    ))
    job.inputs.append(Input(
        source_uri="j3i2source",
        destination_path="j3i2_dest"
    ))
    job.case = CaseSummary(
        id="85b8995c-63a9-474f-8fdc-52c7582ec2ac",
        uri="c1uri",
        label="c1label",
        thumbnail="c1thumbnail",
        description="c1description"
    )
    return job


def new_job4():
    job_id = "eadcd354-a433-48ed-bdc7-e3b2457a1918"
    job = Job(id=job_id)

    job.uri = job_uri_string(job_id)
    job.description = "j4description"
    job.name = "j4name"
    job.status = "j4status"
    job.user = "j4user"
    job.backend_identifier = "j4backend_identifier"

    # emulate the action of sqlalchemy_utils.ArrowType
    # which converts the supplied arrow object UTC
    # when intantiating a job
    job.creation_datetime = j4c_arrow.to("UTC")
    job.start_datetime = j4s_arrow.to("UTC")
    job.end_datetime = j4e_arrow.to("UTC")

    job.families.append(
        Family(
            label="j4f1label",
            name="j4f1name",
            collapse=True,
            parameters=[
                Parameter(help="j4f1p1help",
                          label="j4f1p1label",
                          max_value="j4f1p1max_value",
                          min_value="j4f1p1min_value",
                          name="j4f1p1name",
                          type="j4f1p1type",
                          type_value="j4f1p1type_value",
                          units="j4f1p1units",
                          value="j4f1p1value"),
                Parameter(help="j4f1p2help",
                          label="j4f1p2label",
                          max_value="j4f1p2max_value",
                          min_value="j4f1p2min_value",
                          name="j4f1p2name",
                          type="j4f1p2type",
                          type_value="j4f1p2type_value",
                          units="j4f1p2units",
                          value="j4f1p2value")]
        )
    )

    job.templates.append(Template(
        source_uri="j4t1source",
        destination_path="j4t1_dest"))
    job.templates.append(Template(
        source_uri="j4t2source",
        destination_path="j4t2_dest"
    ))
    job.scripts.append(Script(
        action="RUN",
        source_uri="j4s1source",
        destination_path="j4s1_dest"
    ))
    job.scripts.append(Script(
        action="PROGRESS",
        source_uri="j4s2source",
        destination_path="j4s2_dest"
    ))
    job.scripts.append(Script(
        action="CANCEL",
        source_uri="j4s3source",
        destination_path="j4s1_dest"
    ))
    job.scripts.append(Script(
        action="SETUP",
        source_uri="j4s4source",
        destination_path="j4s4_dest"
    ))
    job.inputs.append(Input(
        source_uri="j4i1source",
        destination_path="j4i1_dest"
    ))
    job.inputs.append(Input(
        source_uri="j4i2source",
        destination_path="j4i2_dest"
    ))
    job.case = CaseSummary(
        id="85b8995c-63a9-474f-8fdc-52c7582ec2ac",
        uri="c1uri",
        label="c1label",
        thumbnail="c1thumbnail",
        description="c1description"
    )
    return job


def new_job5():
    job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    job = Job(id=job_id)

    job.uri = job_uri_string(job_id)
    job.description = "j5description"
    job.name = "j5name"
    job.status = "j5status"
    job.user = "j5user"
    job.backend_identifier = "j5backend_identifier"

    # emulate the action of sqlalchemy_utils.ArrowType
    # which converts the supplied arrow object UTC
    # when intantiating a job
    job.creation_datetime = j5c_arrow.to("UTC")
    job.start_datetime = j5s_arrow.to("UTC")
    job.end_datetime = j5e_arrow.to("UTC")

    job.families.append(
        Family(
            label="j5f1label",
            name="j5f1name",
            collapse=True,
            parameters=[
                Parameter(help="j5f1p1help",
                          label="j5f1p1label",
                          max_value="j5f1p1max_value",
                          min_value="j5f1p1min_value",
                          name="viscosity_phase_1",
                          type="j5f1p1type",
                          type_value="j5f1p1type_value",
                          units="j5f1p1units",
                          value="0.007"),
                Parameter(help="j5f1p2help",
                          label="j5f1p2label",
                          max_value="j5f1p2max_value",
                          min_value="j5f1p2min_value",
                          name="j5f1p2name",
                          type="j5f1p2type",
                          type_value="j5f1p2type_value",
                          units="j5f1p2units",
                          value="j5f1p2value")]
        )
    )

    job.templates.append(Template(
        source_uri="./resources/templates/Blue.nml",
        destination_path="project/case/"))
    job.scripts.append(Script(action="RUN",
        source_uri="./resources/scripts/run_job.sh",
        destination_path="project/case/"))
    job.scripts.append(Script(
        action="PROGRESS",
        source_uri="./resources/scripts/progress_job.sh",
        destination_path="project/case/"))
    job.scripts.append(Script(
        action="CANCEL",
        source_uri="./resources/scripts/cancel_job.sh",
        destination_path="project/case/"))
    job.scripts.append(Script(
        action="SETUP",
        source_uri="./resources/scripts/setup_job.sh",
        destination_path="project/case/"))
    job.inputs.append(Input(
        source_uri="j5i1source",
        destination_path="project/case/"))
    job.inputs.append(Input(
        source_uri="j5i2source",
        destination_path="project/case/"))
    job.case = CaseSummary(
        id="85b8995c-63a9-474f-8fdc-52c7582ec2ac",
        uri="c1uri",
        label="c1label",
        thumbnail="c1thumbnail",
        description="c1description")
    return job


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
        destination_path="j1t1_dest"))
    job.templates.append(TemplateTemplate(
        source_uri="j1t2source",
        destination_path="j1t2_dest"))
    job.scripts.append(ScriptTemplate(
        action="j1s1action",
        source_uri="j1s1source",
        destination_path="j1s1_dest"))
    job.scripts.append(ScriptTemplate(
        action="j1s2action",
        source_uri="j1s2source",
        destination_path="j1s2_dest"))
    job.inputs.append(InputTemplate(
        source_uri="j1i1source",
        destination_path="j1i1_dest"))
    job.inputs.append(InputTemplate(
        source_uri="j1i2source",
        destination_path="j1i2_dest"))
    return job


def new_case1():
    case_id = "85b8995c-63a9-474f-8fdc-52c7582ec2ac"
    case = Case(id=case_id)
    case.uri = "c1uri"
    case.label = "c1label"
    case.thumbnail = "c1thumbnail"
    case.description = "c1description"
    case.job = new_job_template1()
    return case

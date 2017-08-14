from middleware.job.models import Job, Parameter, Template, Script, Input
import arrow

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


def new_job1():
    # NOTE: Ensure to update new_job1_json() to match any changes made here
    job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    job = Job(id=job_id)

    job.description = "j1description"
    job.name = "j1name"
    job.status = "j1status"
    job.status_description = "j1status_description"
    job.user = "j1user"

    job.creation_datetime = j1c_arrow
    job.start_datetime = j1s_arrow
    job.end_datetime = j1e_arrow

    job.parameters.append(Parameter(
        help="j1p1help",
        label="j1p1label",
        max_value="j1p1max_value",
        min_value="j1p1min_value",
        name="j1p1name",
        type="j1p1type",
        type_value="j1p1type_value",
        units="j1p1units",
        value="j1p1value"
        )
    )

    job.parameters.append(Parameter(
        help="j1p2help",
        label="j1p2label",
        max_value="j1p2max_value",
        min_value="j1p2min_value",
        name="j1p2name",
        type="j1p2type",
        type_value="j1p2type_value",
        units="j1p2units",
        value="j1p2value"
        )
    )

    job.templates.append(Template(source_uri="j1t1source",
                                  destination_path="j1t1_dest"))
    job.templates.append(Template(source_uri="j1t2source",
                                  destination_path="j1t2_dest"))
    job.scripts.append(Script(action="j1s1action", source_uri="j1s1source",
                              destination_path="j1s1_dest"))
    job.scripts.append(Script(action="j1s2action", source_uri="j1s2source",
                              destination_path="j1s2_dest"))
    job.inputs.append(Input(source_uri="j1i1source",
                            destination_path="j1i1_dest"))
    job.inputs.append(Input(source_uri="j1i2source",
                            destination_path="j1i2_dest"))
    return job


def new_job1_json():
    # NOTE: Ensure to update new_job1() to match any changes made here
    return {"id": "d769843b-6f37-4939-96c7-c382c3e74b46",
            "description": "j1description",
            "name": "j1name",
            "status": "j1status",
            "status_description": "j1status_description",
            "user": "j1user",
            "creation_datetime": j1c_utc_string,
            "start_datetime": j1s_utc_string,
            "end_datetime": j1e_utc_string,
            "parameters": [{
                    "help": "j1p1help",
                    "label": "j1p1label",
                    "max_value": "j1p1max_value",
                    "min_value": "j1p1min_value",
                    "name": "j1p1name",
                    "type": "j1p1type",
                    "type_value": "j1p1type_value",
                    "units": "j1p1units",
                    "value": "j1p1value"
                },
                {
                    "help": "j1p2help",
                    "label": "j1p2label",
                    "max_value": "j1p2max_value",
                    "min_value": "j1p2min_value",
                    "name": "j1p2name",
                    "type": "j1p2type",
                    "type_value": "j1p2type_value",
                    "units": "j1p2units",
                    "value": "j1p2value"
                }],
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
                        "destination_path": "j1i2_dest"}]}


def new_job2():
    # NOTE: Ensure to update new_job2_json() to match any changes made here
    job_id = "9044394f-de29-4be3-857f-33a4fdca0be3"
    job = Job(id=job_id)

    job.description = "j2description"
    job.name = "j2name"
    job.status = "j2status"
    job.status_description = "j2status_description"
    job.user = "j2user"

    job.creation_datetime = j2c_arrow
    job.start_datetime = j2s_arrow
    job.end_datetime = j2e_arrow

    job.parameters.append(Parameter(
       help="j2p1help",
       label="j2p1label",
       max_value="j2p1max_value",
       min_value="j2p1min_value",
       name="j2p1name",
       type="j2p1type",
       type_value="j2p1type_value",
       units="j2p1units",
       value="j2p1value"
       )
    )
    job.parameters.append(Parameter(
       help="j2p2help",
       label="j2p2label",
       max_value="j2p2max_value",
       min_value="j2p2min_value",
       name="j2p2name",
       type="j2p2type",
       type_value="j2p2type_value",
       units="j2p2units",
       value="j2p2value"
       )
    )

    job.templates.append(Template(source_uri="j2t1source",
                                  destination_path="j2t1_dest"))
    job.templates.append(Template(source_uri="j2t2source",
                                  destination_path="j2t2_dest"))
    job.scripts.append(Script(action="j2s1action", source_uri="j2s1source",
                              destination_path="j2s1_dest"))
    job.scripts.append(Script(action="j2s2action", source_uri="j2s2source",
                              destination_path="j2s2_dest"))
    job.inputs.append(Input(source_uri="j2i1source",
                            destination_path="j2i1_dest"))
    job.inputs.append(Input(source_uri="j2i2source",
                            destination_path="j2i2_dest"))
    return job


def new_job2_json():
    # NOTE: Ensure to update new_job2() to match any changes made here
    return {"id": "9044394f-de29-4be3-857f-33a4fdca0be3",
            "description": "j2description",
            "name": "j2name",
            "status": "j2status",
            "status_description": "j2status_description",
            "user": "j2user",
            "creation_datetime": j2c_utc_string,
            "start_datetime": j2s_utc_string,
            "end_datetime": j2e_utc_string,
            "parameters": [{
                    "help": "j2p1help",
                    "label": "j2p1label",
                    "max_value": "j2p1max_value",
                    "min_value": "j2p1min_value",
                    "name": "j2p1name",
                    "type": "j2p1type",
                    "type_value": "j2p1type_value",
                    "units": "j2p1units",
                    "value": "j2p1value"
                },
                {
                    "help": "j2p2help",
                    "label": "j2p2label",
                    "max_value": "j2p2max_value",
                    "min_value": "j2p2min_value",
                    "name": "j2p2name",
                    "type": "j2p2type",
                    "type_value": "j2p2type_value",
                    "units": "j2p2units",
                    "value": "j2p2value"
                }],
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
                        "destination_path": "j2i2_dest"}]}


def new_job3():
    job_id = "eadcd354-a433-48ed-bdc7-e3b2457a1918"
    job = Job(id=job_id)

    job.description = "j3description"
    job.name = "j3name"
    job.status = "j3status"
    job.status_description = "j3status_description"
    job.user = "j3user"

    job.creation_datetime = j3c_arrow
    job.start_datetime = j3s_arrow
    job.end_datetime = j3e_arrow

    job.parameters.append(Parameter(
       help="j3p1help",
       label="j3p1label",
       max_value="j3p1max_value",
       min_value="j3p1min_value",
       name="j3p1name",
       type="j3p1type",
       type_value="j3p1type_value",
       units="j3p1units",
       value="j3p1value"
       )
    )
    job.parameters.append(Parameter(
       help="j3p2help",
       label="j3p2label",
       max_value="j3p2max_value",
       min_value="j3p2min_value",
       name="j3p2name",
       type="j3p2type",
       type_value="j3p2type_value",
       units="j3p2units",
       value="j3p2value"
       )
    )

    job.templates.append(Template(source_uri="j3t1source",
                                  destination_path="j3t1_dest"))
    job.templates.append(Template(source_uri="j3t2source",
                                  destination_path="j3t2_dest"))
    job.scripts.append(Script(action="j3s1action", source_uri="j3s1source",
                              destination_path="j3s1_dest"))
    job.scripts.append(Script(action="j3s2action", source_uri="j3s2source",
                              destination_path="j3s2_dest"))
    job.inputs.append(Input(source_uri="j3i1source",
                            destination_path="j3i1_dest"))
    job.inputs.append(Input(source_uri="j3i2source",
                            destination_path="j3i2_dest"))
    return job


def new_job4():
    job_id = "eadcd354-a433-48ed-bdc7-e3b2457a1918"
    job = Job(id=job_id)

    job.description = "j4description"
    job.name = "j4name"
    job.status = "j4status"
    job.status_description = "j4status_description"
    job.user = "j4user"

    job.creation_datetime = j4c_arrow
    job.start_datetime = j4s_arrow
    job.end_datetime = j4e_arrow

    job.parameters.append(Parameter(
       help="j4p1help",
       label="j4p1label",
       max_value="j4p1max_value",
       min_value="j4p1min_value",
       name="j4p1name",
       type="j4p1type",
       type_value="j4p1type_value",
       units="j4p1units",
       value="j4p1value"
       )
    )
    job.parameters.append(Parameter(
       help="j4p2help",
       label="j4p2label",
       max_value="j4p2max_value",
       min_value="j4p2min_value",
       name="j4p2name",
       type="j4p2type",
       type_value="j4p2type_value",
       units="j4p2units",
       value="j4p2value"
       )
    )

    job.templates.append(Template(source_uri="j4t1source",
                                  destination_path="j4t1_dest"))
    job.templates.append(Template(source_uri="j4t2source",
                                  destination_path="j4t2_dest"))
    job.scripts.append(Script(action="RUN", source_uri="j4s1source",
                              destination_path="j3s1_dest"))
    job.scripts.append(Script(action="PROGRESS", source_uri="j4s2source",
                              destination_path="j4s2_dest"))
    job.scripts.append(Script(action="CANCEL", source_uri="j4s3source",
                              destination_path="j4s1_dest"))
    job.scripts.append(Script(action="SETUP", source_uri="j4s4source",
                              destination_path="j4s4_dest"))
    job.inputs.append(Input(source_uri="j4i1source",
                            destination_path="j4i1_dest"))
    job.inputs.append(Input(source_uri="j4i2source",
                            destination_path="j4i2_dest"))
    return job


def new_job5():
    job_id = "d769843b-6f37-4939-96c7-c382c3e74b46"
    job = Job(id=job_id)

    job.description = "j5description"
    job.name = "j5name"
    job.status = "j5status"
    job.status_description = "j5status_description"
    job.user = "j5user"

    job.creation_datetime = j5c_arrow
    job.start_datetime = j5s_arrow
    job.end_datetime = j5e_arrow

    job.parameters.append(Parameter(
       help="j5p1help",
       label="j5p1label",
       max_value="j5p1max_value",
       min_value="j5p1min_value",
       name="viscosity_phase_1",
       type="j5p1type",
       type_value="j5p1type_value",
       units="j5p1units",
       value="42.0"
       )
    )

    job.templates.append(Template(source_uri="./resources/templates/Blue.nml",
                                  destination_path="project/case/"))

    job.scripts.append(Script(action="RUN",
                              source_uri="./resources/scripts/start_job.sh",
                              destination_path="project/case/"))
    job.scripts.append(Script(action="PROGRESS",
                              source_uri="./resources/scripts/progress_job.sh",
                              destination_path="project/case/"))
    job.scripts.append(Script(action="CANCEL",
                              source_uri="./resources/scripts/cancel_job.sh",
                              destination_path="project/case/"))
    job.scripts.append(Script(action="SETUP",
                              source_uri="./resources/scripts/setup_job.sh",
                              destination_path="project/case/"))
    job.inputs.append(Input(source_uri="j5i1source",
                            destination_path="project/case/"))
    job.inputs.append(Input(source_uri="j5i2source",
                            destination_path="project/case/"))
    return job

from middleware.database import db
from uuid import uuid4
from sqlalchemy_utils import ArrowType
from config.base import MIDDLEWARE_URL, URI_STEMS


class Case(db.Model):
    id = db.Column(db.String, primary_key=True)

    uri = db.Column(db.String)
    label = db.Column(db.String)
    thumbnail = db.Column(db.String)
    description = db.Column(db.String)

    job_id = db.Column(db.Integer, db.ForeignKey('job_template._id'))
    job = db.relationship("JobTemplate", back_populates="case", lazy="joined")

    # TODO equivalency (__eq__)


class JobTemplate(db.Model):
    # JobTemplate objects have no id field
    # id is assigned when creating a Job object
    _id = db.Column(db.Integer, primary_key=True)
    case = db.relationship("Case", back_populates="job", uselist=False)

    description = db.Column(db.String)
    name = db.Column(db.String)
    user = db.Column(db.String)

    families = db.relationship(
        "FamilyTemplate", back_populates="job", lazy="joined")
    templates = db.relationship(
        "TemplateTemplate", back_populates="job", lazy="joined")
    scripts = db.relationship(
        "ScriptTemplate", back_populates="job", lazy="joined")
    inputs = db.relationship(
        "InputTemplate", back_populates="job", lazy="joined")
    outputs = db.relationship(
        "OutputTemplate", back_populates="job", lazy="joined")

    def __init__(
            self,
            description=None,
            name=None,
            families=[],
            templates=[],
            scripts=[],
            inputs=[],
            outputs=[]):

        # string fields
        self.description = description
        self.name = name

        # list fields
        self.families = families
        self.templates = templates
        self.scripts = scripts
        self.inputs = inputs
        self.outputs = outputs

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.description == other.description and
                    self.name == other.name and
                    sorted(self.families) == sorted(other.families) and
                    sorted(self.templates) == sorted(other.templates) and
                    sorted(self.scripts) == sorted(other.scripts) and
                    sorted(self.inputs) == sorted(other.inputs) and
                    sorted(self.outputs) == sorted(other.outputs)
                    # TODO case equivalency
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class Job(db.Model):
    id = db.Column(db.String, primary_key=True)

    backend_identifier = db.Column(db.String)
    description = db.Column(db.String)
    name = db.Column(db.String)
    status = db.Column(db.String)
    uri = db.Column(db.String)
    user = db.Column(db.String)

    creation_datetime = db.Column(ArrowType)
    start_datetime = db.Column(ArrowType)
    end_datetime = db.Column(ArrowType)

    families = db.relationship(
        "Family", back_populates="job", lazy="joined")
    templates = db.relationship(
        "Template", back_populates="job", lazy="joined")
    scripts = db.relationship(
        "Script", back_populates="job", lazy="joined")
    inputs = db.relationship(
        "Input", back_populates="job", lazy="joined")
    outputs = db.relationship(
        "Output", back_populates="job", lazy="joined")

    case_id = db.Column(db.Integer, db.ForeignKey('case_summary._id'))
    case = db.relationship("CaseSummary", back_populates="jobs", lazy="joined")

    def __init__(
            self,
            id=None,
            backend_identifier=None,
            description=None,
            name=None,
            status="New",
            uri=None,
            user=None,
            creation_datetime=None,
            start_datetime=None,
            end_datetime=None,
            families=[],
            templates=[],
            scripts=[],
            inputs=[],
            outputs=[],
            case=None):

        if id:
            # use id provided
            self.id = id
        else:
            # generate a new id
            self.id = str(uuid4())

        # string fields
        self.backend_identifier = backend_identifier
        self.description = description
        self.name = name
        self.status = status
        self.uri = uri
        self.user = user

        # time fields
        self.creation_datetime = creation_datetime
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

        # list fields
        self.families = families
        self.templates = templates
        self.scripts = scripts
        self.inputs = inputs
        self.outputs = outputs

        self.case = case

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.id == other.id and
                    self.backend_identifier == other.backend_identifier and
                    self.description == other.description and
                    self.name == other.name and
                    self.uri == other.uri and
                    self.user == other.user and
                    self.status == other.status and
                    self.creation_datetime == other.creation_datetime and
                    self.start_datetime == other.start_datetime and
                    self.end_datetime == other.end_datetime and
                    sorted(self.families) == sorted(other.families) and
                    sorted(self.templates) == sorted(other.templates) and
                    sorted(self.scripts) == sorted(other.scripts) and
                    sorted(self.inputs) == sorted(other.inputs) and
                    sorted(self.outputs) == sorted(other.outputs)
                    # TODO case equivalency
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class FamilyTemplate(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_template._id'))
    job = db.relationship("JobTemplate", back_populates="families")

    collapse = db.Column(db.Boolean)
    label = db.Column(db.String)
    name = db.Column(db.String)

    parameters = db.relationship("ParameterTemplate", back_populates="family",
                                 lazy="joined")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.collapse == other.collapse and
                self.label == other.label and
                self.name == other.name and
                sorted(self.parameters) == sorted(other.parameters)
            )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((
            self.collapse,
            self.label,
            self.name,
        ))


class Family(db.Model):
    _id = db.Column(db.Integer, primary_key=True)

    collapse = db.Column(db.Boolean)
    label = db.Column(db.String)
    name = db.Column(db.String)

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="families")

    parameters = db.relationship("Parameter", back_populates="family",
                                 lazy="joined")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.collapse == other.collapse and
                self.label == other.label and
                self.name == other.name and
                sorted(self.parameters) == sorted(other.parameters)
            )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((
            self.collapse,
            self.label,
            self.name,
        ))


class ParameterTemplate(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family_template._id'))
    family = db.relationship("FamilyTemplate", back_populates="parameters")

    enabled = db.Column(db.Boolean)

    help = db.Column(db.String)
    label = db.Column(db.String)
    max_value = db.Column(db.String)
    min_value = db.Column(db.String)
    step = db.Column(db.String)
    name = db.Column(db.String)
    type = db.Column(db.String)
    type_value = db.Column(db.String)
    units = db.Column(db.String)
    value = db.Column(db.String)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.enabled == other.enabled and
                self.help == other.help and
                self.label == other.label and
                self.max_value == other.max_value and
                self.min_value == other.min_value and
                self.step == other.step and
                self.name == other.name and
                self.type == other.type and
                self.type_value == other.type_value and
                self.units == other.units and
                self.value == other.value)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((
            self.enabled,
            self.help,
            self.label,
            self.max_value,
            self.min_value,
            self.step,
            self.name,
            self.type,
            self.type_value,
            self.units,
            self.value))


class Parameter(db.Model):
    _id = db.Column(db.Integer, primary_key=True)

    enabled = db.Column(db.Boolean)

    help = db.Column(db.String)
    label = db.Column(db.String)
    max_value = db.Column(db.String)
    min_value = db.Column(db.String)
    step = db.Column(db.String)
    name = db.Column(db.String)
    type = db.Column(db.String)
    type_value = db.Column(db.String)
    units = db.Column(db.String)
    value = db.Column(db.String)

    family_id = db.Column(db.Integer, db.ForeignKey('family._id'))
    family = db.relationship("Family", back_populates="parameters")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.enabled == other.enabled and
                self.help == other.help and
                self.label == other.label and
                self.max_value == other.max_value and
                self.min_value == other.min_value and
                self.step == other.step and
                self.name == other.name and
                self.type == other.type and
                self.type_value == other.type_value and
                self.units == other.units and
                self.value == other.value)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((
            self.enabled,
            self.help,
            self.label,
            self.max_value,
            self.min_value,
            self.step,
            self.name,
            self.type,
            self.type_value,
            self.units,
            self.value))


class TemplateTemplate(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job_template._id'))
    job = db.relationship("JobTemplate", back_populates="templates")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.source_uri == other.source_uri and
                    self.destination_path == other.destination_path
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.source_uri, self.destination_path))


class Template(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="templates")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.source_uri == other.source_uri and
                    self.destination_path == other.destination_path
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.source_uri, self.destination_path))


class ScriptTemplate(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)

    job_id = db.Column(db.Integer, db.ForeignKey('job_template._id'))
    job = db.relationship("JobTemplate", back_populates="scripts")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.action == other.action and
                    self.source_uri == other.source_uri and
                    self.destination_path == other.destination_path
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.action, self.source_uri, self.destination_path))


class Script(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="scripts")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.action == other.action and
                    self.source_uri == other.source_uri and
                    self.destination_path == other.destination_path
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.action, self.source_uri, self.destination_path))


class InputTemplate(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job_template._id'))
    job = db.relationship("JobTemplate", back_populates="inputs")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.source_uri == other.source_uri and
                    self.destination_path == other.destination_path
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.source_uri, self.destination_path))


class Input(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="inputs")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.source_uri == other.source_uri and
                    self.destination_path == other.destination_path
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.source_uri, self.destination_path))


class OutputTemplate(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    destination_path = db.Column(db.String)
    type = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job_template._id'))
    job = db.relationship("JobTemplate", back_populates="outputs")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.destination_path == other.destination_path and
                    self.type == other.type)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.destination_path, self.type))


class Output(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    destination_path = db.Column(db.String)
    type = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="outputs")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.destination_path == other.destination_path and
                    self.type == other.type)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.destination_path, self.type))


class CaseSummary(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String)
    jobs = db.relationship("Job", back_populates="case")

    uri = db.Column(db.String)
    label = db.Column(db.String)
    thumbnail = db.Column(db.String)
    description = db.Column(db.String)

    # TODO equivalency (__eq__)


def get_attribute_list(model):
    attribute_list = \
        [a for a in vars(model) if not a.startswith('_')]
    return attribute_list


# Model conversion utilites
def parameter_template_to_parameter(parameter_template):
    parameter = Parameter()
    attribute_list = get_attribute_list(parameter_template)
    for attribute in attribute_list:
        source = getattr(parameter_template, attribute)
        setattr(parameter, attribute, source)
    return parameter


def family_template_to_family(family_template):
    family = Family()

    family.label = family_template.label
    family.name = family_template.name
    family.collapse = family_template.collapse

    for parameter_template in family_template.parameters:
        family.parameters.append(
            parameter_template_to_parameter(parameter_template)
        )

    return family


def template_template_to_template(template_template):
    template = Template()
    attribute_list = get_attribute_list(template_template)
    for attribute in attribute_list:
        source = getattr(template_template, attribute)
        setattr(template, attribute, source)
    return template


def script_template_to_script(script_template):
    script = Script()
    attribute_list = get_attribute_list(script_template)
    for attribute in attribute_list:
        source = getattr(script_template, attribute)
        setattr(script, attribute, source)
    return script


def input_template_to_input(input_template):
    input_ = Input()
    attribute_list = get_attribute_list(input_template)
    for attribute in attribute_list:
        source = getattr(input_template, attribute)
        setattr(input_, attribute, source)
    return input_


def output_template_to_output(output_template):
    output_ = Output()
    attribute_list = get_attribute_list(output_template)
    for attribute in attribute_list:
        source = getattr(output_template, attribute)
        setattr(output_, attribute, source)
    return output_


def case_to_job(case, job_id=None):
    job = Job(job_id)
    job.description = case.job.description
    job.name = case.job.name
    job.user = case.job.user
    job.uri = "{}{}/{}".format(MIDDLEWARE_URL,
                               URI_STEMS['jobs'],
                               job.id)

    job.case = CaseSummary(
        id=case.id,
        uri=case.uri,
        label=case.label,
        thumbnail=case.thumbnail,
        description=case.description
    )

    for family_template in case.job.families:
        job.families.append(family_template_to_family(family_template))

    for template_template in case.job.templates:
        job.templates.append(template_template_to_template(template_template))

    for script_template in case.job.scripts:
        job.scripts.append(script_template_to_script(script_template))

    for input_template in case.job.inputs:
        job.inputs.append(input_template_to_input(input_template))

    for output_template in case.job.outputs:
        job.outputs.append(output_template_to_output(output_template))

    return job


def copy_job_fields(source, destination, fields):
    for field in fields:
        try:
            # Set all ignored fields on new job equal to field value in old job
            setattr(destination, field, getattr(source, field))
        except Exception as e:
            print(e)
    return destination

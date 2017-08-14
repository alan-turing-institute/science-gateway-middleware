from middleware.database import db
from uuid import uuid4
from sqlalchemy_utils import ArrowType


class Job(db.Model):
    id = db.Column(db.String, primary_key=True)

    description = db.Column(db.String)
    name = db.Column(db.String)
    status = db.Column(db.String)
    status_description = db.Column(db.String)
    user = db.Column(db.String)

    creation_datetime = db.Column(ArrowType)
    start_datetime = db.Column(ArrowType)
    end_datetime = db.Column(ArrowType)

    parameters = db.relationship("Parameter", back_populates="job",
                                 lazy="joined")
    templates = db.relationship("Template", back_populates="job",
                                lazy="joined")
    scripts = db.relationship("Script", back_populates="job",
                              lazy="joined")
    inputs = db.relationship("Input", back_populates="job",
                             lazy="joined")

    def __init__(
            self,
            id=None,
            description=None,
            name=None,
            status=None,
            status_description=None,
            user=None,
            creation_datetime=None,
            start_datetime=None,
            end_datetime=None,
            parameters=[],
            templates=[],
            scripts=[],
            inputs=[]):
        if id is not None:
            self.id = id
        else:
            self.id = str(uuid4())

        # string fields
        self.description = description
        self.name = name
        self.status = status
        self.status_description = status_description
        self.user = user

        # time fields
        self.creation_datetime = creation_datetime
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

        self.parameters = parameters
        self.templates = templates
        self.scripts = scripts
        self.inputs = inputs

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.id == other.id and
                    self.description == other.description and
                    self.name == other.name and
                    self.status == other.status and
                    self.status_description == other.status_description and
                    self.user == other.user and
                    self.creation_datetime == other.creation_datetime and
                    self.start_datetime == other.start_datetime and
                    self.end_datetime == other.end_datetime and
                    sorted(self.parameters) == sorted(other.parameters) and
                    sorted(self.templates) == sorted(other.templates) and
                    sorted(self.scripts) == sorted(other.scripts) and
                    sorted(self.inputs) == sorted(other.inputs)
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class Parameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    help = db.Column(db.String)
    label = db.Column(db.String)
    max_value = db.Column(db.String)
    min_value = db.Column(db.String)
    name = db.Column(db.String)
    type = db.Column(db.String)
    type_value = db.Column(db.String)
    units = db.Column(db.String)
    value = db.Column(db.String)

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="parameters")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.help == other.help and
                self.label == other.label and
                self.max_value == other.max_value and
                self.min_value == other.min_value and
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
            self.help,
            self.label,
            self.max_value,
            self.min_value,
            self.name,
            self.type,
            self.type_value,
            self.units,
            self.value))


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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


class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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


class Input(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

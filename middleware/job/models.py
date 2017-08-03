from middleware.database import db
from copy import deepcopy
from uuid import uuid4


class Job(db.Model):
    id = db.Column(db.String, primary_key=True)
    user = db.Column(db.String)
    parameters = db.relationship("Parameter", back_populates="job")
    templates = db.relationship("Template", back_populates="job")
    scripts = db.relationship("Script", back_populates="job")
    inputs = db.relationship("Input", back_populates="job")

    def __init__(self, id=None):
        if id is not None:
            self.id = id
        else:
            self.id = str(uuid4())

    def __deepcopy__(self, memo):
        new_job = Job()
        new_job.user = self.user
        new_job.parameters = deepcopy(self.parameters, memo)
        new_job.templates = deepcopy(self.templates, memo)
        new_job.scripts = deepcopy(self.scripts, memo)
        new_job.inputs = deepcopy(self.inputs, memo)
        return new_job


class Parameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    value = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="parameters")

    def __deepcopy__(self, memo):
        new_parameter = Parameter()
        new_parameter.name = self.name
        new_parameter.value = self.value
        return new_parameter


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="templates")

    def __deepcopy__(self, memo):
        new_template = Template()
        new_template.source_uri = self.source_uri
        new_template.destination_path = self.destination_path
        return new_template


class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.String)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="scripts")

    def __deepcopy__(self, memo):
        new_script = Script()
        new_script.command = self.command
        new_script.source_uri = self.source_uri
        new_script.destination_path = self.destination_path
        return new_script


class Input(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="inputs")

    def __deepcopy__(self):
        new_input = Input()
        new_input.source_uri = self.source_uri
        new_input.destination_path = self.destination_path

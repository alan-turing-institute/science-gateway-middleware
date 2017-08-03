#!/usr/bin/env python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from marshmallow import Schema, fields

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.String, primary_key=True)
    user = db.Column(db.String)
    parameters = db.relationship("Parameter", back_populates="job")
    templates = db.relationship("Template", back_populates="job")
    scripts = db.relationship("Script", back_populates="job")
    inputs = db.relationship("Input", back_populates="job")


class Parameter(db.Model):
    __tablename__ = 'parameter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    value = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="parameters")


class Template(db.Model):
    __tablename__ = 'template'
    id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String, nullable=False)
    destination_path = db.Column(db.String, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="templates")

class Script(db.Model):
    __tablename__ = 'script'
    id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String, nullable=False)
    destination_path = db.Column(db.String, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="scripts")


class Input(db.Model):
    __tablename__ = 'input'
    id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String, nullable=False)
    destination_path = db.Column(db.String, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="inputs")

class ParameterSchema(Schema):
    name = fields.String()
    value = fields.String()

class TemplateSchema(Schema):
    source_uri = fields.String()
    destination_path = fields.String()

class ScriptSchema(Schema):
    source_uri = fields.String()
    destination_path = fields.String()

class InputSchema(Schema):
    source_uri = fields.String()
    destination_path = fields.String()

class JobSchema(Schema):
    id = fields.String()
    user = fields.String()
    parameters = fields.List(fields.Nested(ParameterSchema))
    templates = fields.List(fields.Nested(TemplateSchema))
    scripts = fields.List(fields.Nested(ScriptSchema))
    inputs = fields.List(fields.Nested(InputSchema))

db.create_all()


# <codecell>

my_parameter_1 = Parameter(name="viscosity_phase_1", value="0.004")
my_parameter_2 = Parameter(name="viscosity_phase_2", value="0.07")

my_template = Template(source_uri='./resources/templates/Blue.nml', destination_path='project/case/')
my_script = Script(source_uri='./resources/scripts/start_job.sh', destination_path='project/case/')
my_input = Input(source_uri='./resources/inputs/mesh_file.stl', destination_path='project/case/')

my_job = Job(id="d769843b-6f37-4939-96c7-c382c3e74b46", user="lrmason", parameters=[my_parameter_1, my_parameter_2], templates=[my_template], scripts=[my_script], inputs=[my_input])

# <codecell>

# parameter_schema = ParameterSchema()
# template_schema = TemplateSchema()
# script_schema = ScriptSchema()
# input_schema = InputSchema()
job_schema = JobSchema()

# template_schema.dump(my_template).data
# script_schema.dump(my_script).data
# input_schema.dump(my_input).data
print(job_schema.dump(my_job).data)

# # <codecell>
#
db.session.add(my_job)
db.session.commit()

# j = Job.query.filter_by(id="abc-123").first()
# j.scripts[0].destination_path
# j.id

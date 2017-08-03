from middleware.core import db


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
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="templates")

class Script(db.Model):
    __tablename__ = 'script'
    id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="scripts")


class Input(db.Model):
    __tablename__ = 'input'
    id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="inputs")

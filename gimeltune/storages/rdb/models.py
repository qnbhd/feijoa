from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, ForeignKey, PickleType
from sqlalchemy.orm import relationship

_Base = declarative_base()


class JobModel(_Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f'Job<{self.id}, {self.name}'


class ExperimentModel(_Base):
    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True)
    job_id = Column(ForeignKey(JobModel.id), primary_key=True)
    job = relationship(JobModel, backref='models')
    state = Column(String)
    hash = Column(String)
    objective_result = Column(Float)
    params = Column(PickleType)
    requestor = Column(String)
    create_timestamp = Column(Float)
    finish_timestamp = Column(Float)
    metrics = Column(PickleType)

# MIT License
#
# Copyright (c) 2021-2022 Templin Konstantin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""SQLAlchemy models module."""

import json

from sqlalchemy import Column, Float, ForeignKey, Integer, String, TypeDecorator, types
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship

__all__ = [
    "SearchSpaceModel",
    "ParameterModel",
    "JobModel",
    "ExperimentModel",
]


_Base: DeclarativeMeta = declarative_base()


class Json(TypeDecorator):  # type: ignore
    """Json column (temporary class)."""

    @property
    def python_type(self):
        return object

    impl = types.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_literal_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return None


class SearchSpaceModel(_Base):  # type: ignore
    __tablename__ = "search_space"

    id = Column(Integer, primary_key=True)


class ParameterModel(_Base):  # type: ignore
    __tablename__ = "parameter"

    id = Column(Integer, primary_key=True)
    search_space_id = Column(ForeignKey(SearchSpaceModel.id))  # type: ignore
    search_space = relationship(SearchSpaceModel, backref="parameters")  # type: ignore

    name = Column(String)
    kind = Column(String)
    meta = Column(Json)


class JobModel(_Base):  # type: ignore
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    search_space_id = Column(ForeignKey(SearchSpaceModel.id))  # type: ignore
    search_space = relationship(SearchSpaceModel, backref="jobs")  # type: ignore
    last_optimizer = Column(String)

    def __repr__(self):
        return f"Job<{self.id}, {self.name}"


class ExperimentModel(_Base):  # type: ignore
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True)
    job_id = Column(ForeignKey(JobModel.id), primary_key=True)  # type: ignore
    job = relationship(JobModel, backref="experiments")  # type: ignore
    state = Column(String)
    hash = Column(String)
    objective_result = Column(Float)
    requestor = Column(String)
    params = Column(Json)
    create_timestamp = Column(Float)
    finish_timestamp = Column(Float)
    metrics = Column(Json)

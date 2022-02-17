import datetime
import hashlib
import json
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel


class MetricNotExists(Exception):
    """Raises if metric not in result"""


class ExperimentState(str, Enum):
    OK = 'OK'
    WIP = 'WIP'
    ERROR = 'ERROR'
    SEMI = 'SEMI'


class Experiment(BaseModel):
    """
    Pipeline:

    1) Create experiment from params (state=WIP)
    2) Suggest experiment to job
    3) Measure it
    4) If all metrics are collected set OK state,
    therefore SEMI state, if error caused - ERROR.
    5) Finish experiment - calculate hash, set finish
    timestamp
    6) Tell to optimizers
    6) Save to storage
    """

    id: int
    job_id: int
    state: ExperimentState
    hash: Optional[str]
    objective_result: Optional[Any]
    params: Dict[str, Any]
    requestor: str
    create_timestamp: float
    finish_timestamp: Optional[float]

    def __repr__(self):
        return f'Experiment({json.dumps(self.dict(), indent=4)})'

    def __str__(self):
        return repr(self)

    def is_ok(self):
        return self.state == ExperimentState.OK

    def _calculate_hash(self):
        params_dumped = json.dumps(self.params, sort_keys=True)

        curve1 = hashlib.sha1(params_dumped.encode())
        curve2 = hashlib.sha1(str(self.objective_result).encode())

        hd1 = curve1.hexdigest()
        hd2 = curve2.hexdigest()

        return hd1 + hd2

    def success_finish(self):
        self.state = ExperimentState.OK
        self.hash = self._calculate_hash()

        time = datetime.datetime.now()
        self.finish_timestamp = datetime.datetime.timestamp(time)


class ExperimentsFactory:

    def __init__(self, job):
        self.job = job

    def create(self, params):
        time = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(time)

        return Experiment(id=self.job.experiments_count + 1,
                          job_id=self.job.id,
                          state=ExperimentState.WIP,
                          requestor='UNKNOWN',
                          create_timestamp=timestamp,
                          params=params)

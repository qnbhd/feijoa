import datetime
import json
from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from polytune.search.renderer import Renderer
from polytune.search.space import SearchSpace

import hashlib


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
    metrics: Dict[str, Any]
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
        metrics_dumped = json.dumps(self.metrics, sort_keys=True)

        curve1 = hashlib.sha1(params_dumped.encode())
        curve2 = hashlib.sha1(metrics_dumped.encode())

        hd1 = curve1.hexdigest()
        hd2 = curve2.hexdigest()

        return hd1 + hd2

    def success_finish(self):
        self.state = ExperimentState.OK
        self.hash = self._calculate_hash()

        time = datetime.datetime.now()
        self.finish_timestamp = datetime.datetime.timestamp(time)

    def get_metric(self, metric_name: str):
        try:
            result = self.metrics.get(metric_name, None)
        except KeyError:
            raise MetricNotExists()

        return result

    def __getitem__(self, item):
        return self.get_metric(item)

    def render(self, space: SearchSpace, renderer_cls: Type[Renderer]) -> str:
        renderer = renderer_cls(self)

        rendered = list()

        for p_name in self.metrics.keys():
            p = space.get_by_name(p_name)
            result = p.accept(renderer)
            rendered.append(result)

        return " ".join(rendered)


class ExperimentsFactory:

    def __init__(self, job):
        self.job = job

    def create(self, params):
        time = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(time)

        return Experiment(id=self.job.experiments_count + 1,
                          job_id=self.job.job_id,
                          state=ExperimentState.WIP,
                          create_timestamp=timestamp,
                          metrics=dict(),
                          params=params)

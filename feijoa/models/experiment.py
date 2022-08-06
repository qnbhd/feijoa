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
"""Experiment model class module."""

import datetime
from enum import Enum
import hashlib
import json
from typing import Any
from typing import Optional

from pydantic import BaseModel

from feijoa.models.configuration import Configuration


__all__ = ["ExperimentState", "Experiment"]


class ExperimentState(str, Enum):

    OK = "OK"
    WIP = "WIP"
    ERROR = "ERROR"

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)


# noinspection PyUnresolvedReferences
class Experiment(BaseModel):
    """Experiment model.

    Lifecycle of experiment:

    1) Create experiment from params (state=WIP)
    2) Suggest experiment to job
    3) Measure it
    4) If all metrics are collected set OK state,
       if error caused - ERROR.
    5) Finish experiment - calculate hash, set finish
       timestamp
    6) Tell to optimizers
    6) Save to storage

    Args:
        id (int):
            Index of experiment.
        job_id (int):
            Job index.
        state (ExperimentState):
            Experiment state. Must be `WIP`, `OK` or `ERROR`
        hash (str, optional):
            Hash of experiment.
        objective_result (Optional[Any]):
            Objective result of experiment. Now
            is float only, but in next version
            can be tuple/array.
        create_timestamp (float):
            Experiment creation timestamp.
        finish_timestamp (float):
            Experiment finish timestamp.
        metrics (dict, optional):
            Metrics of experiment.

    Raises:
        AnyError: If anything bad happens.

    """

    id: int
    job_id: int
    state: ExperimentState
    hash: Optional[str]
    objective_result: Optional[Any]
    params: Configuration
    create_timestamp: float
    finish_timestamp: Optional[float]
    metrics: Optional[dict]

    class Config:
        orm_mode = True

    def apply(self, result):
        """Apply result to experiment.

        Args:
            result (float):
                Objective result.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        # TODO (qnbhd): make safe operations
        self.objective_result = result

    def set_error(self):
        """Set error state to experiment."""

        self.state = ExperimentState.ERROR

    def is_finished(self):
        """Check if experiment is finished."""

        return (
            self.state == ExperimentState.OK
            or self.state == ExperimentState.ERROR
        )

    def _calculate_hash(self):
        """Calculate hash."""

        params_dumped = json.dumps(self.params, sort_keys=True)

        curve1 = hashlib.sha1(params_dumped.encode())
        curve2 = hashlib.sha1(str(self.objective_result).encode())

        hd1 = curve1.hexdigest()
        hd2 = curve2.hexdigest()

        return hd1 + hd2

    def _finish(self, state):
        """Finish experiment."""

        self.state = state
        self.hash = self._calculate_hash()

        time = datetime.datetime.now()
        self.finish_timestamp = datetime.datetime.timestamp(time)

    def success_finish(self):
        """Finish experiment with success state."""

        self._finish(ExperimentState.OK)

    def error_finish(self):
        """Finish experiment with error state."""

        self._finish(ExperimentState.ERROR)

    def __repr__(self):
        return f"Experiment({json.dumps(self.dict(), indent=4)})"

    def __str__(self):
        return repr(self)

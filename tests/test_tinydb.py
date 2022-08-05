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
import unittest.mock

from feijoa import Experiment
from feijoa import Real
from feijoa import SearchSpace

# noinspection DuplicatedCode
from feijoa.exceptions import DBVersionError
from feijoa.exceptions import InsertExperimentWithTheExistedId
from feijoa.models.configuration import Configuration
from feijoa.models.experiment import ExperimentState
from feijoa.utils.imports import import_or_skip
import pytest


TinyDBStorage = import_or_skip("feijoa.storages.tiny").TinyDBStorage


def test_tiny_db_version_check():
    TinyDBStorage("boo.json")

    with unittest.mock.patch.object(
        TinyDBStorage, "__version__", "0.1.1"
    ):
        with pytest.raises(DBVersionError):
            TinyDBStorage("boo.json")


def test_insert_experiment_with_the_same_id():
    storage = TinyDBStorage("woo.json")

    ex = Experiment(
        id=0,
        job_id=0,
        state=ExperimentState.WIP,
        create_timestamp=0.0,
        params=Configuration({"x": 0.0, "y": 1.0}),
    )

    ex_duplicated = Experiment(
        id=0,
        job_id=0,
        state=ExperimentState.WIP,
        create_timestamp=0.0,
        params=Configuration({"x": 0.0, "y": 1.0}),
    )

    storage.insert_experiment(ex)

    with pytest.raises(InsertExperimentWithTheExistedId):
        storage.insert_experiment(ex_duplicated)

    assert storage.get_experiment(0, 1000) is None


def test_load_job_by_id():
    storage = TinyDBStorage("simple.json")

    class _Job:
        def __init__(self, job_id, job_name):
            self.id = job_id
            self.name = job_name
            self.search_space = SearchSpace()
            self.search_space.insert(Real("x", low=0.0, high=1.0))
            self.search_space.insert(Real("y", low=0.0, high=1.0))

    job = _Job(0, "foo")

    storage.insert_job(job)

    assert storage.get_job_id_by_name("foo") == 0

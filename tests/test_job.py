from typing import List, Optional

import pytest

from feijoa import Experiment, Real, SearchSpace, create_job, load_job
from feijoa.exceptions import (
    DuplicatedJobError,
    InvalidStoragePassed,
    InvalidStorageRFC1738,
    JobNotFoundError,
    SearchOracleNotFoundedError,
)

# noinspection PyProtectedMember
from feijoa.jobs.job import _load_storage
from feijoa.models import Result


def test_job():
    job = create_job(search_space=SearchSpace())

    job.setup_default_algo()

    assert job.best_experiment is None
    assert job.best_value is None
    assert job.best_parameters is None
    assert isinstance(job.experiments, list) and not job.experiments
    assert job.experiments_count == 0
    assert job.top_experiments(10) == []
    assert job.dataframe.empty


def test_create_load_job():
    space = SearchSpace()
    space.insert(Real("x", low=0.0, high=1.0))
    space.insert(Real("y", low=0.0, high=1.0))

    def objective(experiment: Experiment):
        params = experiment.params

        x = params.get("x")
        y = params.get("y")

        metrics = {
            "foo": 1.0,
            "bar": 2.0,
        }

        obj = (1 - x) ** 2 + (1 - y) ** 2

        return Result(objective_result=obj, metrics=metrics)

    job = create_job(search_space=space, name="foo", storage="sqlite:///foo.db")
    job.do(objective, n_trials=10, optimizer="ucb<random>")

    assert isinstance(job.experiments, list) and len(job.experiments) == 10
    assert job.experiments_count == 10
    assert len(job.top_experiments(100)) == 10

    print(job.dataframe)

    job2 = load_job(name="foo", storage="sqlite:///foo.db")

    assert isinstance(job2.experiments, list) and len(job2.experiments) == 10
    assert job2.experiments_count == 10
    assert len(job2.top_experiments(100)) == 10

    print(job2.get_dataframe(desc=True))


def test_incorrect_oracle_passed():
    space = SearchSpace()
    job = create_job(search_space=space)

    with pytest.raises(SearchOracleNotFoundedError):
        job.do(lambda: 1, optimizer="ucb<some_incorrect>")


def test_job_duplicated_error():
    create_job(
        search_space=SearchSpace(),
        name="foo",
        storage="sqlite:///foo.db",
    )

    with pytest.raises(DuplicatedJobError):
        create_job(
            search_space=SearchSpace(),
            name="foo",
            storage="sqlite:///foo.db",
        )


def test_load_non_existed():

    with pytest.raises(JobNotFoundError):
        load_job(name="dimple", storage="sqlite:///:memory:")


def test_load_storage():
    with pytest.raises(InvalidStorageRFC1738):
        _load_storage("dfddsfdsfsd")

    with pytest.raises(InvalidStoragePassed):
        _load_storage(dict(a=1))

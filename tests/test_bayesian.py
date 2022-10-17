import random

import numpy as np

from feijoa import Categorical
from feijoa import create_job
from feijoa import Integer
from feijoa import Real
from feijoa import SearchSpace
from feijoa.search.oracles.bayesian import Bayesian


def test_bayesian():
    space = SearchSpace()
    space.insert(Real("x", low=0.0, high=1.0))
    space.insert(Integer("y", low=0, high=1))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    oracle = Bayesian(space)

    np.random.seed(0)
    random.seed(0)

    expected_configurations = [
        {"x": 0.8444218515250481, "y": 1, "z": "foo"},
        {"x": 0.25891675029296335, "y": 1, "z": "bar"},
        {"x": 0.9182343317851318, "y": 1, "z": "bar"},
        {"x": 0.3580493746949883, "y": 0, "z": "foo"},
        {"x": 0.28183784439970383, "y": 0, "z": "bar"},
        {"x": 0.014009789835700115, "y": 1, "z": "bar"},
        {"x": 0.3086521036815205, "y": 0, "z": "foo"},
        {"x": 0.7852669966261011, "y": 0, "z": "foo"},
        {"x": 0.11577567447740011, "y": 0, "z": "foo"},
    ]

    fetched_configurations = []

    for i in range(5):
        configurations = map(dict, oracle.ask(1))
        for config in configurations:
            fetched_configurations.append(config)
            # noinspection PyTypeChecker
            oracle.tell(config, 1.0)

    assert fetched_configurations == expected_configurations


def test_bayesian_search():
    space = SearchSpace()

    space.insert(Integer("x", low=0, high=2))
    space.insert(Real("y", low=0.0, high=0.5))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    def objective(experiment):
        x = experiment.params.get("x")
        y = experiment.params.get("y")
        z = experiment.params.get("z")

        return -(x + y + (2 if z == "foo" else 3))

    job = create_job(search_space=space)
    job.do(objective, n_trials=10, optimizer="ucb<bayesian>")


# noinspection DuplicatedCode
def test_specify_acq_bayesian_search():
    space = SearchSpace()

    space.insert(Integer("x", low=0, high=2))
    space.insert(Real("y", low=0.0, high=0.5))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    def objective(experiment):
        x = experiment.params.get("x")
        y = experiment.params.get("y")
        z = experiment.params.get("z")

        return -(x + y + (2 if z == "foo" else 3))

    job = create_job(search_space=space)
    job.do(
        objective,
        n_trials=10,
        optimizer="ucb<bayesian[acq_function=ei]>",
    )

    job = create_job(search_space=space)
    job.do(
        objective,
        n_trials=10,
        optimizer="ucb<bayesian[acq_function=poi]>",
    )

    job = create_job(search_space=space)
    job.do(
        objective,
        n_trials=10,
        optimizer="ucb<bayesian[acq_function=ucb]>",
    )

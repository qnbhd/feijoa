from feijoa import create_job
from feijoa import Experiment
from feijoa import Real
from feijoa import SearchSpace

# noinspection DuplicatedCode
from feijoa.search.oracles.bayesian import Bayesian
from feijoa.search.oracles.meta.bandit import ThompsonSampler


def objective(experiment: Experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    return (
        (1.5 - x + x * y) ** 2
        + (2.25 - x + x * y**2) ** 2
        + (2.625 - x + x * y**3) ** 2
    )


def test_minimal():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=5.0))
    space.insert(Real("y", low=0.0, high=2.0))

    job = create_job(search_space=space)
    job.do(
        objective,
        n_trials=50,
        optimizer="ucb<template,bayesian>",
    )

    assert abs(job.best_value - 0) < 5


def test_job_with_oracle_ensemble():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=5.0))
    space.insert(Real("y", low=0.0, high=2.0))

    job = create_job(search_space=space)

    job.do(
        objective,
        n_trials=50,
        optimizer="""ucb<template,
                     bayesian[regressor=RandomForestRegressor],
                     bayesian[acq_function=ucb]>""",
    )

    assert abs(job.best_value - 0) < 5
    assert len(job.dataframe) == 50

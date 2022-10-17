import logging

import numpy as np
import pytest

from feijoa import Real, SearchSpace, create_job

log = logging.getLogger(__name__)


def test_different_optimizers():
    def f(experiment):
        x, y = experiment.params["x"], experiment.params["y"]
        return x + np.cos(y)

    space = SearchSpace(Real("x", low=0.0, high=1.0), Real("y", low=0.0, high=1.0))

    job = create_job(search_space=space)
    job.do(f, n_trials=5, optimizer="ucb<bayesian,random>")
    job = create_job(search_space=space)
    job.do(f, n_trials=5, optimizer="th<bayesian,random>")
    job = create_job(search_space=space)
    job.do(f, n_trials=5, optimizer="th<bayesian,pattern>")

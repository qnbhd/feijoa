import logging

from feijoa import create_job
from feijoa import Real
from feijoa import SearchSpace
from feijoa.exceptions import InvalidOptimizer
from feijoa.search import RoundRobinMeta
from feijoa.search.algorithms.grid import GridSearch
from feijoa.search.algorithms.templatesearch import (
    TemplateSearchAlgorithm,
)
from feijoa.search.bandit import ThompsonSampler
from feijoa.search.bandit import UCB1
from feijoa.search.bandit import UCBTuned
import numpy as np
import pytest


log = logging.getLogger(__name__)


def test_different_optimizers():
    def f(experiment):
        x, y = experiment.params["x"], experiment.params["y"]
        return x + np.cos(y)

    space = SearchSpace(
        Real("x", low=0.0, high=1.0), Real("y", low=0.0, high=1.0)
    )

    create_job(search_space=space, optimizer=RoundRobinMeta)
    create_job(search_space=space, optimizer=UCB1)

    with pytest.raises(InvalidOptimizer):
        create_job(search_space=space, optimizer=1)

    grid = GridSearch(search_space=space)
    template = TemplateSearchAlgorithm(search_space=space)
    template1 = TemplateSearchAlgorithm(search_space=space)

    op1 = RoundRobinMeta(grid, template)
    op2 = UCB1(template, grid, template1)
    op3 = UCBTuned(grid, template)

    ensemble = ThompsonSampler(op1, op2, op3)

    job = create_job(search_space=space, optimizer=ensemble)
    job.do(objective=f, n_proc=5, n_trials=20, clear=False)

    print(job.best_parameters)
    print(job.rewards)

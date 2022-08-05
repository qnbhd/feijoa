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

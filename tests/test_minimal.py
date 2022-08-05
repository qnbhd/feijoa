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
from feijoa import create_job
from feijoa import Experiment
from feijoa import Real
from feijoa import SearchSpace

# noinspection DuplicatedCode
from feijoa.search.algorithms.bayesian import BayesianAlgorithm
from feijoa.search.bandit import ThompsonSampler
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor


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
    job.do(objective, n_trials=50)

    assert abs(job.best_value - 0) < 5
    assert len(job.dataframe) == 50


def test_job_with_algo_ensemble():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=5.0))
    space.insert(Real("y", low=0.0, high=2.0))

    job = create_job(search_space=space, optimizer=ThompsonSampler)

    ada = BayesianAlgorithm(
        search_space=space, regressor=AdaBoostRegressor
    )
    forest = BayesianAlgorithm(
        search_space=space, regressor=RandomForestRegressor
    )
    classic = BayesianAlgorithm(search_space=space)

    classic.name = "ClassicBayesianSearch"
    mlp = BayesianAlgorithm(
        search_space=space, regressor=MLPRegressor
    )

    job.do(
        objective,
        n_trials=50,
        algo_list=["template", ada, forest, classic, mlp],
    )

    assert abs(job.best_value - 0) < 5
    assert len(job.dataframe) == 50

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
def test_seed():
    space = SearchSpace()
    space.insert(Real("x", low=0.0, high=1.0))
    space.insert(Real("y", low=0.0, high=1.0))

    def objective(experiment: Experiment):
        params = experiment.params

        x = params.get("x", 5.0)
        y = params.get("y", 5.0)

        return (1 - x) ** 2 + (1 - y) ** 2

    job = create_job(search_space=space)
    job.add_seed({"x": 1.0, "y": 1.0})
    job.do(objective, n_trials=50, n_proc=1, algo_list=["grid"])

    assert job.best_parameters == {"x": 1.0, "y": 1.0}
    # assert job.best_experiment.requestor == "SeedAlgorithm"

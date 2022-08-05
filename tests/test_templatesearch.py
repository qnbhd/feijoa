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
from feijoa import Categorical
from feijoa import create_job
from feijoa import Experiment
from feijoa import Integer
from feijoa import Real
from feijoa import SearchSpace


def objective(experiment: Experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    z = experiment.params.get("z")

    a = 0
    if z == "foo":
        a = 1
    if z == "bar":
        a = -1

    return (
        (1.5 - x + x * y) ** 2
        + (2.25 - x + x * y**2) ** 2
        + (2.625 - x + x * y**3) ** 2
        + a
    )


def test_template_search():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=5.0))
    space.insert(Integer("y", low=0, high=2))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    job = create_job(search_space=space)
    job.do(objective, n_trials=200, algo_list=["template"])

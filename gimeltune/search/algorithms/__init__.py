# MIT License
#
# Copyright (c) 2021 Templin Konstantin
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

from ...exceptions import SearchAlgorithmNotFoundedError
from .algorithm import SearchAlgorithm
from .bayesian import BayesianAlgorithm
from .grid import GridSearch
from .randomized import RandomSearch
from .seed import SeedAlgorithm
from .skopt import SkoptBayesianAlgorithm
from .templatesearch import TemplateSearchAlgorithm

registry = {}


def register(algo_name, algo_cls, *algo_aliases):
    registry[algo_name] = algo_cls

    for alias in algo_aliases:
        registry[alias] = algo_cls


register("skopt", SkoptBayesianAlgorithm, "Skopt")
register("bayesian", BayesianAlgorithm, "bayes, Bayesian")
register("seed", SeedAlgorithm, "Seed")
register("random", RandomSearch, "Random", "RandomSearch")
register("grid", GridSearch, "Grid", "GridSearch")
register("template", TemplateSearchAlgorithm, "template-search",
         "basic-template")


def get_algo(algo_name):
    algo = registry.get(algo_name, None)

    if not algo:
        raise SearchAlgorithmNotFoundedError()

    return algo

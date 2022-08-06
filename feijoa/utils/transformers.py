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
import numpy as np

from feijoa import Categorical
from feijoa import Integer
from feijoa import Real


def transform(sol, search_space):
    """Transform solutions into a dictionary.

    Args:
        sol (list | numpy.array):
            Vector of parameter's values.
        search_space:
            Search space instance.

    Raises:
        AnyError: If anything bad happens.

    """

    configuration = dict()

    for value, param in zip(sol, search_space):
        if isinstance(param, Real):
            configuration[param.name] = value
            continue

        rounded = int(value + (0.5 if value > 0 else -0.5))

        if isinstance(param, Integer):
            configuration[param.name] = rounded
        elif isinstance(param, Categorical):
            configuration[param.name] = param.choices[rounded]

    return configuration


def inverse_transform(configuration: dict, search_space):
    """Transform dictionary (configuration)
    to vector of parameter's values.

    Args:
        configuration (dict | Configuration):
            Feijoa configuration.
        search_space:
            Search space instance.

    Raises:
        AnyError: If anything bad happens.

    """

    solution = np.zeros((len(configuration),), dtype=np.float64)

    for i, (key, value) in enumerate(configuration.items()):
        param = search_space.get(key)

        if isinstance(param, Real):
            solution[i] = value

        if isinstance(param, Integer):
            solution[i] = value

        if isinstance(param, Categorical):
            index = param.choices.index(value)
            solution[i] = index

    return solution

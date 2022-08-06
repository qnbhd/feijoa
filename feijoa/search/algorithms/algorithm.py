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
"""Base class of search algorithms."""

import abc
from typing import List
from typing import Optional

from feijoa.models.configuration import Configuration


__all__ = ["SearchAlgorithm"]


class SearchAlgorithm(metaclass=abc.ABCMeta):
    """Base class of search algorithms.

    Have a simple ask-tell interface.

    When creating the possibility of implementing
    algorithms, it is desirable that the constructor
    arguments should not contain any dependencies on
    feijoa, except for SearchSpace. This decision is
    made to keep the algorithms easy to use without
    initializing feijoa components.

    All algorithms must implement:

        anchor:
            Name of algorithm, which
            used for dynamic searching all algorithms
            in project.

        aliases:
            synonyms for algorithm name.

        ask(n):
            Get k <= n configurations.

        tell(configuration, result):
            Tell algorithm measured result for
            configuration


    Raises:
        AnyError: If anything bad happens.

    """

    def __init__(self, *args, **kwargs):
        self._name = self.__class__.__name__

    @property
    @abc.abstractmethod
    def anchor(self):
        """Name used for dynamic algorithm detection."""

        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def aliases(self):
        """Synonyms for algorithm name."""

        raise NotImplementedError()

    @abc.abstractmethod
    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        """Get configurations from algorithm.

        Args:
            n (int, optional):
                Preferred count of configurations.

        .. note::
            Parameter **n** may not affect on
            configuration's count.

        Returns:
            List of configurations, or None if
            configurations are over.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def tell(self, config, result):
        """Tell configuration's result to algorithm
        to accumulate information model.

        Args:
            config (Configuration):
                Configuration instance.
            result (float):
                Objective result for configuration.

        .. note::
            The function signature may change in the
            future due to plans to implement
            multi&many-objective optimization.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @property
    def name(self):
        """Name of algorithm."""

        return self._name

    @name.setter
    def name(self, v):
        """Name setter for algorithm."""

        self._name = v

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
"""Base class of search oracles."""

import abc
import random
from typing import List, Optional

import numpy

from feijoa.models.configuration import Configuration

__all__ = ["Oracle"]

from feijoa.utils.mixins import Observer, Subject


class Oracle(Subject, Observer, metaclass=abc.ABCMeta):
    """
    Base class of search oracles.

    Have a simple ask-tell interface.

    When creating the possibility of implementing
    oracles, it is desirable that the constructor
    arguments should not contain any dependencies on
    feijoa, except for SearchSpace. This decision is
    made to keep the oracles easy to use without
    initializing feijoa components.

    All oracles must implement:

        anchor:
            Name of oracle, which
            used for dynamic searching all oracles
            in project.

        aliases:
            synonyms for oracle name.

        ask(n):
            Get k <= n configurations.

        tell(configuration, result):
            Tell oracle measured result for
            configuration


    Raises:
        AnyError: If anything bad happens.

    """

    def __init__(self, *args, seed=0, **kwargs):
        self._name = self.__class__.__name__
        self.subscribers = []
        numpy.random.seed(seed)
        random.seed(seed)
        self.seed = seed

    @property
    @abc.abstractmethod
    def anchor(self):
        """Name used for dynamic oracle detection."""

        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def aliases(self):
        """Synonyms for oracle name."""

        raise NotImplementedError()

    @abc.abstractmethod
    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        """
        Get configurations from oracle.

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
        """
        Tell configuration's result to oracle
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
        """Name of oracle."""

        return self._name

    @name.setter
    def name(self, v):
        """Name setter for oracle."""

        self._name = v

    def attach(self, observer: Observer) -> None:
        self.subscribers.append(observer)

    def detach(self, observer: Observer) -> None:
        self.subscribers.remove(observer)

    def notify(self, event, *args, **kwargs):
        for observer in self.subscribers:
            observer.update(event, self, *args, **kwargs)

    def update(self, event, subject, *args, **kwargs):
        pass

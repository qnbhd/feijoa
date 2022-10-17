import abc
from typing import Tuple

import feijoa


class Problem(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def n_iterations(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def space(self) -> feijoa.SearchSpace:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def solution(self) -> Tuple[dict, float]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def start_points(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def evaluate(self, x):
        raise NotImplementedError()

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
import abc
from typing import List
from typing import Optional


__all__ = ["SearchAlgorithm"]

from feijoa.models.configuration import Configuration


class SearchAlgorithm(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def anchor(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def aliases(self):
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        self._name = self.__class__.__name__

    @abc.abstractmethod
    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        raise NotImplementedError()

    @abc.abstractmethod
    def tell(self, config, result):
        raise NotImplementedError()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, v):
        self._name = v

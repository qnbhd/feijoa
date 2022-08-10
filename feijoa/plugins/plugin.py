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
"""Base plugin's class module."""

from abc import ABCMeta

from feijoa.utils.mixins import Observer
from feijoa.utils.mixins import Subject


__all__ = ["Plugin"]


class Plugin(Observer, Subject, metaclass=ABCMeta):
    """
    Base plugin's class.

    The idea of plugins is to optionally add
    new functionality to search oracles.
    The plugin inherits from the Subject and
    Observer classes. This means that he can
    be both a subject (receive notification
    from oracle), as well as an observer
    (send alerts to oracle).

    Args:
        subscribers (list):
            Initial array of subscribers.

    Raises:
        AnyError: If anything bad happens.

    """

    @property
    def anchor(self):
        raise NotImplementedError()

    @property
    def aliases(self):
        raise NotImplementedError()

    def __init__(self, subscribers=None):
        self.subscribers = subscribers or list()

    def attach(self, observer: Observer) -> None:
        self.subscribers.append(observer)

    def detach(self, observer: Observer) -> None:
        self.subscribers.remove(observer)

    def notify(self, event, *args, **kwargs) -> None:
        for o in self.subscribers:
            o.update(event, self, *args, **kwargs)

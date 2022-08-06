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
"""Base importance evaluator class module."""

import abc

from feijoa.jobs.job import Job


__all__ = ["ImportanceEvaluator"]


class ImportanceEvaluator(metaclass=abc.ABCMeta):
    """
    Base importance evaluator.

    Measures the excessive amount of hyperparameter
    taken per feature value. Helps to select only the most
    influential hyperparameters for their tuning.
    Does not require additional measurements.

    .. note::
        This version does not apply the study of the influence
        of a combination of hyperparameters.
    """

    @abc.abstractmethod
    def do(self, job: Job):
        """
        Calculate hyperparameters importance.

        Args:
            job (Job) : Specified job.

        Returns:
            Dict with keys `params` and `importances`
                `params` contains names of parameters,
                `importances` contains list of importances.

        Raises:
            AnyError: If anything bad happens.
        """

        raise NotImplementedError()

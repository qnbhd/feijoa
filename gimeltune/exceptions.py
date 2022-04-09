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

__all__ = [
    'DBVersionError',
    'SearchAlgorithmNotFoundedError',
    'DuplicatedJobError',
    'JobNotFoundError',
    'ExperimentNotFinishedError',
]


class GimeltuneError(Exception):
    """Common class for gimeltune exceptions."""


class DBVersionError(GimeltuneError):
    """
    Raises if the loaded storage version
    does not match the current version
    """


class SearchAlgorithmNotFoundedError(GimeltuneError):
    """
    Raises if the chosen search algorithm
    not founded.
    """


class DuplicatedJobError(GimeltuneError):
    """
    Raises if the specified job name already
    exists in the storage.
    """


class JobNotFoundError(GimeltuneError):
    """
    Raises if the specified job name not
    exists in the storage.
    """


class ExperimentNotFinishedError(GimeltuneError):
    """
    Raises if an attempt was made to inform
    the search algorithms that the experiment
    was not completed. To complete the experiment,
    you must call the .success_finish() method
    """


class ParametersIncorrectInputValues(GimeltuneError):
    """
    Raises if incorrect values passed to parameter's constructor.
    """
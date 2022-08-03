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
    "DBVersionError",
    "SearchAlgorithmNotFoundedError",
    "DuplicatedJobError",
    "JobNotFoundError",
    "ExperimentNotFinishedError",
    "ParametersIncorrectInputValues",
    "InsertExperimentWithTheExistedId",
    "InvalidStoragePassed",
    "InvalidStorageRFC1738",
    "PackageNotInstalledError",
    "InvalidOptimizer",
]


class FeijoaError(Exception):
    """Common class for feijoa exceptions."""


class DBVersionError(FeijoaError):
    """
    Raises if the loaded storage version
    does not match the current version
    """


class SearchAlgorithmNotFoundedError(FeijoaError):
    """
    Raises if the chosen search algorithm
    not founded.
    """


class DuplicatedJobError(FeijoaError):
    """
    Raises if the specified job name already
    exists in the storage.
    """


class JobNotFoundError(FeijoaError):
    """
    Raises if the specified job name not
    exists in the storage.
    """


class ExperimentNotFinishedError(FeijoaError):
    """
    Raises if an attempt was made to inform
    the search algorithms that the experiment
    was not completed. To complete the experiment,
    you must call the .success_finish() method
    """


class ParametersIncorrectInputValues(FeijoaError):
    """
    Raises if incorrect values passed to parameter's constructor.
    """


class InsertExperimentWithTheExistedId(FeijoaError):
    """
    Raises if the specified experiment with current id
    is already exists in db storage.
    """


class InvalidStoragePassed(FeijoaError):
    """Raises if the specified object is not a storage."""


class InvalidStorageRFC1738(FeijoaError):
    """Raises if you could not parse rfc1738 URL
    from specified string."""


class InvalidOptimizer(FeijoaError):
    """Raises if specified optimizer class doesn't
    inherit from MetaSearchAlgorithm"""


class PackageNotInstalledError(FeijoaError):
    """Raises if an attempt to import a package
    was not successful"""

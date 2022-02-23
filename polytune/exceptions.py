
__all__ = [
    'DBVersionError',
    'SearchAlgorithmNotFoundedError'
]


class PolytuneError(Exception):
    """Common class for polytune exceptions."""


class DBVersionError(PolytuneError):
    """
    Raises if the loaded storage version
    does not match the current version
    """


class SearchAlgorithmNotFoundedError(PolytuneError):
    """
    Raises if the chosen search algorithm
    not founded.
    """


class DuplicatedJobError(PolytuneError):
    """
    Raises if the specified job name already
    exists in the storage.
    """


class JobNotFoundError(PolytuneError):
    """
    Raises if the specified job name not
    exists in the storage.
    """


class ExperimentNotFinishedError(PolytuneError):
    """
    Raises if an attempt was made to inform
    the search algorithms that the experiment
    was not completed. To complete the experiment,
    you must call the .success_finish() method
    """
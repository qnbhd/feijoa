import abc

from feijoa.jobs.job import Job


class ImportanceEvaluator(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def do(self, job: Job):
        raise NotImplementedError()

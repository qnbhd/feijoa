from typing import List, Optional

from polytune.jobs.job import Experiment


class Storage:
    def insert(self, cfg, result):
        raise NotImplementedError()

    def hash_is_exists(self, h):
        raise NotImplementedError()

    def best_configuration(self, objective):
        raise NotImplementedError()

    def get_result(self, cfg):
        raise NotImplementedError()

    def results_list(self):
        raise NotImplementedError()


import abc


class StorageV2(metaclass=abc.ABCMeta):

    def insert_job(self, job):
        """

        :param job:
        :return:
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def is_job_name_exists(self, name):
        """

        :param name:
        :return:
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_job_id_by_name(self, name) -> Optional[int]:
        """

        :param name:
        :return:
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def insert_experiment(self, experiment):
        """

        :param experiment:
        :return:
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_experiment_by_id(self, experiment_id):
        """

        :param job:
        :param experiment_id:
        :return:
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_experiments_by_job_id(self, job_id) -> List[Experiment]:
        """

        :param job_id:
        :return:
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_experiments_count(self, job) -> int:
        """

        :param job:
        :return:
        """

        pass

    def best_experiment(self, job) -> Optional[Experiment]:
        """

        :param job:
        :return:
        """

        experiments = self.get_experiments_by_job_id(job)

        if not experiments:
            return None

        return min(experiments, key=lambda x: x.objective_result)

    def top_experiments(self, job_id, n) -> Optional[List[Experiment]]:
        """

        :param job_id:
        :param n:
        :return:
        """

        experiments = self.get_experiments_by_job_id(job_id)

        # TODO (qnbhd): Optional??
        if not experiments:
            return None

        experiments.sort(key=lambda x: x.objective_result)
        return experiments[:min(len(experiments) - 1, n)]

    @property
    @abc.abstractmethod
    def jobs(self):
        raise NotImplementedError()

    @property
    def jobs_count(self):
        return len(self.jobs)

    @property
    @abc.abstractmethod
    def version(self):
        raise NotImplementedError()


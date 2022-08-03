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

from feijoa.models import Experiment
from feijoa.search.space import SearchSpace


__all__ = ["Storage"]


class Storage(metaclass=abc.ABCMeta):
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
    def get_experiment(self, job_id, experiment_id):
        """

        :param job_id:
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
    def get_experiments_count(self, job_id) -> int:
        """

        :param job_id:
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

        return min(experiments, key=lambda x: x.objective_result)  # type: ignore

    def top_experiments(self, job_id, n) -> List[Experiment]:
        """

        :param job_id:
        :param n:
        :return:
        """

        experiments = self.get_experiments_by_job_id(job_id)

        experiments.sort(key=lambda x: x.objective_result)  # type: ignore
        return experiments[: min(len(experiments), n)]

    def get_search_space_by_job_id(self, job_id) -> SearchSpace:
        """

        :param job_id:
        """

        raise NotImplementedError()

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

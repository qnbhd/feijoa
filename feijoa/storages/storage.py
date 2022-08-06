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
import abc
from typing import List
from typing import Optional

from feijoa.models import Experiment
from feijoa.search.space import SearchSpace


__all__ = ["Storage"]


class Storage(metaclass=abc.ABCMeta):
    def insert_job(self, job):
        """Insert job into storage.

        Args:
            job (Job):
                Job instance.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def is_job_name_exists(self, name):
        """Find job in storage.

        Args:
            name (str):
                Job name.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_job_id_by_name(self, name) -> Optional[int]:
        """Get job by id in storage.

        Args:
            name (str):
                Name of job.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def insert_experiment(self, experiment):
        """Insert experiment into storage.

        Args:
            experiment (Experiment):
                Experiment instance to insert.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_experiment(self, job_id, experiment_id):
        """Get experiment from job.

        Args:
            job_id (int):
                Job index.
            experiment_id (int):
                Experiment index.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_experiments_by_job_id(self, job_id) -> List[Experiment]:
        """Get experiments from job

        Args:
            job_id:
                Index of job in storage.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def get_experiments_count(self, job_id) -> int:
        """Get experiments count in specified job.

        Args:
            job_id (int):
                Job id.

        Raises:
            AnyError: If anything bad happens.

        """

        pass

    def best_experiment(self, job) -> Optional[Experiment]:
        """Get best experiment from job.

        Args:
            job (Job):
                Job instance.

        Raises:
            AnyError: If anything bad happens.

        """

        experiments = self.get_experiments_by_job_id(job)

        if not experiments:
            return None

        return min(experiments, key=lambda x: x.objective_result)  # type: ignore

    def top_experiments(self, job_id, n) -> List[Experiment]:
        """Get top experiments from job.
        Experiments is sorted by objective values.

        Args:
            job_id (int):
                Job index.

        Raises:
            AnyError: If anything bad happens.

        """

        experiments = self.get_experiments_by_job_id(job_id)

        experiments.sort(key=lambda x: x.objective_result)  # type: ignore
        return experiments[: min(len(experiments), n)]

    def get_search_space_by_job_id(self, job_id) -> SearchSpace:
        """Get search space from existed job.

        Args:
            job_id (int):
                Job index.

        Raises:
            AnyError: If anything bad happens.

        """

        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def jobs(self):
        """Pick up jobs from storage."""

        raise NotImplementedError()

    @property
    def jobs_count(self):
        """Get jobs count from storage."""

        return len(self.jobs)

    @property
    @abc.abstractmethod
    def version(self):
        """Get version of database schema."""

        raise NotImplementedError()

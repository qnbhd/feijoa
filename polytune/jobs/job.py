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
import random
import warnings
from datetime import datetime
from typing import Any, Callable, List, Optional, Type, Union

import multiprocess as mp
import pandas as pd

from polytune.exceptions import DuplicatedJobError, JobNotFoundError, ExperimentNotFinishedError, \
    SearchAlgorithmNotFoundedError
from polytune.models import Experiment, ExperimentsFactory
from polytune.search import Optimizer, SearchSpace
from polytune.search.algorithms import (GridSearch, RandomSearch,
                                        SearchAlgorithm, SeedAlgorithm,
                                        SkoptBayesianAlgorithm, get_algo)
from polytune.storages import Storage, TinyDBStorage

__all__ = [
    'create_job',
    'load_job'
]


class Job:

    """
    Facade of framework.
    """

    def __init__(self, name: str, storage: Storage,
                 search_space: SearchSpace, job_id: int,
                 pruners: Any = None):

        self.name = name
        self.storage = storage
        self.pruners = pruners
        self.id = job_id

        self.experiments_factory = ExperimentsFactory(self)
        self.optimizer = Optimizer(search_space, self.experiments_factory)
        self.search_space = search_space

        self.seeds = []

        if not self.storage.is_job_name_exists(self.name):
            self.storage.insert_job(self)

    @property
    def best_parameters(self) -> Optional[dict]:
        """
        Get the best parameters in job.
        Load configurations with result
        and take params from best.

        :return: the best parameters' dict.
        """

        return self.best_experiment.params \
            if self.best_experiment else None

    @property
    def best_value(self) -> Optional[Any]:
        """
        Get the best result value by objective.

        :return: float best value.
        """

        return self.best_experiment.objective_result \
            if self.best_experiment else None

    @property
    def best_experiment(self) -> Optional[Experiment]:
        """
        Get the best experiment from job.

        :return: best experiment.
        """

        return self.storage.best_experiment(self.id)

    @property
    def experiments(self) -> List[Experiment]:
        """
        Get all experiments.

        :return:
        """

        return self.storage.get_experiments_by_job_id(self.id)

    @property
    def experiments_count(self) -> int:
        """

        :return:
        """

        return self.storage.get_experiments_count(self.id)

    def top_experiments(self, n: int):
        """
        Get top-n experiments by objective.

        :param n: max number of experiments.
        :return: list of experiments
        """

        return self.storage.top_experiments(self.id, n)

    def setup_default_algo(self):
        self.add_algorithm(
            SkoptBayesianAlgorithm(self.search_space, self.experiments_factory))

    def do(self, objective: Callable,
           n_trials: int = 100, n_proc: int = 1,
           algo_list: List[Union[str, Type[SearchAlgorithm]]] = None):

        """
        :param objective: objective function
        :param n_trials: count of max trials.
        :param n_proc: max number of processes.
        :param algo_list: chosen search algorithm's list.
        :return: None
        """

        # noinspection PyPep8Naming

        if self.seeds:
            self.add_algorithm(
                SeedAlgorithm(self.experiments_factory, *self.seeds))

        if not algo_list:
            self.add_algorithm(
                SkoptBayesianAlgorithm(self.search_space, self.experiments_factory))
        else:
            for algo in algo_list:
                if isinstance(algo, str):
                    try:
                        algo_cls = get_algo(algo)
                    except SearchAlgorithmNotFoundedError:
                        raise SearchAlgorithmNotFoundedError()
                elif issubclass(algo, SearchAlgorithm):
                    algo_cls = algo

                # TODO (qnbhd): fix 'Local variable 'algo_cls'
                #  might be referenced before assignment'
                if algo_cls == SkoptBayesianAlgorithm:

                    self.add_algorithm(
                        SkoptBayesianAlgorithm(self.search_space, self.experiments_factory))

                elif algo_cls == RandomSearch:

                    self.add_algorithm(
                        RandomSearch(self.search_space, self.experiments_factory))

                elif algo_cls == GridSearch:

                    self.add_algorithm(
                        GridSearch(self.search_space, self.experiments_factory))
                else:
                    raise SearchAlgorithmNotFoundedError()

        trials = 0

        while trials < n_trials:

            configurations = self.ask()

            if not configurations:
                warnings.warn('No new configurations.')
                # TODO (qnbhd): make closing
                break

            trials += len(configurations)

            # noinspection PyUnresolvedReferences
            with mp.Pool(n_proc) as p:
                results = p.map(objective, configurations)

            # Applying result
            for experiment, result in zip(configurations, results):
                experiment.apply(result)

            # Finishing
            for experiment in configurations:
                experiment.success_finish()
                self.tell(experiment)

    def tell(self, experiment: Experiment):
        """
        Finish concrete experiment.

        :return:
        :raises:
        """

        if experiment.is_finished():
            self.experiments_factory.experiment_is_done()
            self.optimizer.tell(experiment)
            self.storage.insert_experiment(experiment)
            return

        raise ExperimentNotFinishedError()

    def ask(self) -> Optional[List[Experiment]]:
        """
        Ask for a new experiment.
        :return:
        """

        return self.optimizer.ask()

    def export(self, format_: str = ''):
        """

        :param format_:
        :return:
        """
        pass

    @property
    def dataframe(self):

        container = []

        for experiment in self.experiments:
            dataframe_dict = experiment.dict()
            metrics = dataframe_dict.pop('params')

            dataframe_dict['create_time'] = \
                datetime.fromtimestamp(dataframe_dict['create_timestamp'])

            dataframe_dict['finish_time'] = \
                datetime.fromtimestamp(dataframe_dict['finish_timestamp'])

            del dataframe_dict['create_timestamp']
            del dataframe_dict['finish_timestamp']

            container.append({**dataframe_dict, **metrics})

        return pd.DataFrame(container)

    def add_algorithm(self, algo: SearchAlgorithm):
        self.optimizer.add_algorithm(algo)

    def add_seed(self, seed):
        self.seeds.append(seed)


def create_job(search_space: SearchSpace, name: str = None,
               storage: Union[str, Optional[Storage]] = None):

    """

    :param search_space:
    :param name:
    :param storage:
    :return:
    """

    name = name or f'test_job_{random.randint(0, 9999)}'

    if not storage:
        storage = TinyDBStorage(f'{name}.json')
    else:
        if isinstance(storage, str):
            storage = TinyDBStorage(f'{storage}.json')

    assert isinstance(name, str)
    assert isinstance(search_space, SearchSpace)
    assert issubclass(type(storage), Storage)

    if storage.is_job_name_exists(name):
        raise DuplicatedJobError(f'Job {name} is already exists.')

    return Job(name, storage, search_space, storage.jobs_count + 1)


def load_job(search_space: SearchSpace, name: str,
             storage: Union[str, Storage]):

    """

    :param search_space:
    :param name:
    :param storage:
    :return:
    """

    if isinstance(storage, str):
        storage = TinyDBStorage(f'{storage}.json')

    job_id = storage.get_job_id_by_name(name)

    if not job_id:
        raise JobNotFoundError(f'Job {name} not found is storage.')

    experiments = storage.get_experiments_by_job_id(job_id)

    job = Job(name, storage, search_space, job_id)

    for experiment in experiments:
        job.tell(experiment)

    return job

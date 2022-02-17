import random
import warnings
import multiprocess as mp
from typing import Any, Callable, List, Optional, Union

from polytune.search.algorithms import SearchAlgorithm, SkoptBayesianAlgorithm, SeedAlgorithm
from polytune.models import Experiment, ExperimentsFactory
from polytune.search import Optimizer, SearchSpace
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

        return self.best_experiment.metrics \
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
        Load all experiments.

        :return:
        """

        return self.storage.get_experiments_by_job_id(self.id)

    @property
    def experiments_count(self) -> int:
        """

        :return:
        """

        return self.storage.get_experiments_count(self.id)

    def top_configurations(self, n: int):
        """

        :param n:
        :return:
        """
        return self.storage.top_experiments(self.id, n)

    def do(self, metric_collector: Callable, objective: Callable,
           n_trials: int = 100, n_proc: int = 1):

        """

        :param metric_collector:
        :param objective:
        :param n_trials:
        :param n_proc:
        :return:
        """

        # noinspection PyPep8Naming

        if self.seeds:
            self.add_algorithm(
                SeedAlgorithm(self.experiments_factory, *self.seeds))

        if not self.optimizer.algorithms:
            self.add_algorithm(
                SkoptBayesianAlgorithm(self.search_space, self.experiments_factory))

        for it in range(n_trials):

            configurations = self.ask()
            print(configurations)

            if not configurations:
                warnings.warn('No new configurations.')
                raise Exception()

            # noinspection PyUnresolvedReferences
            with mp.Pool(n_proc) as p:
                metrics_list = p.map(metric_collector, configurations)

            print(it)
            print(list(metrics_list))

            for experiment, metrics in zip(configurations, metrics_list):
                experiment.metrics = metrics
                experiment.objective_result = objective(experiment)
                experiment.success_finish()

                self.tell(experiment)
                self.storage.insert_experiment(experiment)

    def tell(self, experiment: Experiment):
        """
        Finish concrete experiment.

        :return:
        :raises:
        """

        if experiment.is_ok():
            self.optimizer.tell(experiment)
            return

        # TODO (qnbhd): refine exception type
        raise Exception()

    def ask(self) -> Optional[List[Experiment]]:
        """

        :return:
        """

        return self.optimizer.ask()

    def export(self, format_: str = ''):
        """

        :param format_:
        :return:
        """
        pass

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
        # TODO (qnbhd): refine exception type
        raise Exception()

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
        # TODO (qnbhd): refine exception type
        raise Exception()

    experiments = storage.get_experiments_by_job_id(job_id)

    job = Job(name, storage, search_space, job_id)

    for experiment in experiments:
        job.tell(experiment)

    return job

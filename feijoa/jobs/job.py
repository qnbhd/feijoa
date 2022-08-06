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
"""Job class module."""

import contextlib
from datetime import datetime
from functools import partial
import inspect
import logging
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Type
from typing import Union
import warnings

import joblib
import numpy as np
import pandas as pd
from rich.progress import Progress
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ArgumentError

from feijoa.exceptions import DuplicatedJobError
from feijoa.exceptions import ExperimentNotFinishedError
from feijoa.exceptions import InvalidOptimizer
from feijoa.exceptions import InvalidSearchAlgorithmPassed
from feijoa.exceptions import InvalidStoragePassed
from feijoa.exceptions import InvalidStorageRFC1738
from feijoa.exceptions import JobNotFoundError
from feijoa.exceptions import SearchAlgorithmNotFoundedError
from feijoa.models import Experiment
from feijoa.models import Result
from feijoa.models.experiment import ExperimentState
from feijoa.search import SearchSpace
from feijoa.search.algorithms import get_algo
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.algorithms.bayesian import BayesianAlgorithm
from feijoa.search.bandit import ThompsonSampler
from feijoa.search.meta import MetaSearchAlgorithm
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Real
from feijoa.search.seed import SeedAlgorithm
from feijoa.storages import Storage
from feijoa.storages.rdb.storage import RDBStorage


__all__ = ["Job", "create_job", "load_job"]

from feijoa.utils.imports import ImportWrapper


log = logging.getLogger(__name__)


class Job:
    """Facade of framework, contains main logic
    of optimization process.

    Example:

        .. code-block:: python

            from feijoa.jobs import Job
            from feijoa.storages.rdb.storage import RDBStorage
            from feijoa.search.space import SearchSpace
            from feijoa.search.bandit import ThompsonSampler

            job = Job(
                name="foo_job",
                storage=RDBStorage("sqlite:///:memory:"),
                search_space=SearchSpace(),
                job_id=1,
                optimizer=ThompsonSampler,
            )

    Args:
        name (str):
            Name of job.
        storage (Storage):
            Storage instance, which will be used to save the results
        search_space (SearchSpace):
            Search space of optimization problem.
        optimizer (MetaSearchAlgorithm):
            Optimizer, which will be used to algorithms manipulation.

    Raises:
        AnyError: If anything bad happens.

    """

    def __init__(
        self,
        name: str,
        storage: Storage,
        search_space: SearchSpace,
        job_id: int,
        pruners: Any = None,
        optimizer=ThompsonSampler,
    ):

        self.name = name
        self.storage = storage
        self.pruners = pruners
        self.id = job_id

        if issubclass(type(optimizer), MetaSearchAlgorithm):
            self.optimizer = optimizer
        elif not issubclass(
            type(optimizer), MetaSearchAlgorithm
        ) and (
            not inspect.isclass(optimizer)
            or not issubclass(optimizer, MetaSearchAlgorithm)
        ):
            raise InvalidOptimizer()
        else:
            self.optimizer = optimizer()

        self.search_space = search_space
        self.pending_experiments = 0

        self.seeds: List[dict] = []

        if not self.storage.is_job_name_exists(self.name):
            self.storage.insert_job(self)

    @property
    def best_parameters(self) -> Optional[dict]:
        """
        Get the best parameters in job.
        Load configurations with result
        and take params from best.

        Returns:
            The best parameters' dict.

        Raises:
            AnyError: If anything bad happens.

        """

        return (
            self.best_experiment.params
            if self.best_experiment
            else None
        )

    @property
    def best_value(self) -> Optional[Any]:
        """
        Get the best result value by objective.

        Returns:
            Float best objective function value.

        Raises:
            AnyError: If anything bad happens.

        """

        return (
            self.best_experiment.objective_result
            if self.best_experiment
            else None
        )

    @property
    def best_experiment(self) -> Optional[Experiment]:
        """
        Get the best experiment from job.

        Returns:
            Best experiment of optimization session.

        Raises:
            AnyError: If anything bad happens.

        """

        return self.storage.best_experiment(self.id)

    @property
    def experiments(self) -> List[Experiment]:
        """
        Get all experiments.

        Returns:
            List of experiments.

        Raises:
            AnyError: If anything bad happens.

        """

        return self.storage.get_experiments_by_job_id(self.id)

    @property
    def experiments_count(self) -> int:
        """
        Get job experiments count.

        Returns:
            Experiments count.

        Raises:
            AnyError: If anything bad happens.
        """

        return self.storage.get_experiments_count(self.id)

    def top_experiments(self, n: int):
        """
        Get top-n experiments by objective.

        Args:
            n (int):
                Max count of top experiments.

        Returns:
            List of top-experiments sorted by objective value.

        Raises:
            AnyError: If anything bad happens.

        """

        return self.storage.top_experiments(self.id, n)

    @property
    def rewards(self):
        """
        Obtaining the results of a strictly
        monotonically decreasing sequence for
        objective function values.

        Returns:
            Length of monotonically decreasing
            sequence for objective function values

        Raises:
            AnyError: If anything bad happens.

        """

        rewards = 0
        experiments = self.experiments
        m = float("+inf")

        for exp in experiments:
            if exp.objective_result < m:
                rewards += 1
                m = exp.objective_result

        return rewards

    def setup_default_algo(self):
        """
        Setup default optimization algorithm (bayesian).

        Raises:
            AnyError: If anything bad happens.

        """

        self.add_algorithm(BayesianAlgorithm(self.search_space))

    def _load_algo(self, algo_list=None):
        """
        Inject algorithms from algo_list to
        current job.

        Args:
            algo_list (List[Union[str, SearchAlgorithm, Type[SearchAlgorithm]]):
                array of algorithms.

        Raises:
            SearchAlgorithmNotFoundedError:
                If passed the name of an algorithm that does not exist.
            InvalidSearchAlgorithmPassed:
                If passes not valid search algorithm.
            AnyError: If anything bad happens.

        """

        if self.seeds:
            self.add_algorithm(SeedAlgorithm(*self.seeds))

        if not algo_list:
            self.add_algorithm(BayesianAlgorithm(self.search_space))
        else:
            for algo in algo_list:
                if isinstance(algo, str):
                    try:
                        algo_cls = get_algo(algo)
                    except SearchAlgorithmNotFoundedError:
                        raise SearchAlgorithmNotFoundedError()
                elif isinstance(algo, SearchAlgorithm):
                    self.add_algorithm(algo)
                    continue
                elif issubclass(algo, SearchAlgorithm):
                    algo_cls = algo
                else:
                    raise InvalidSearchAlgorithmPassed()

                # noinspection PyArgumentList
                self.add_algorithm(
                    algo_cls(search_space=self.search_space)
                )

    def do(
        self,
        objective: Callable,
        n_trials: int = 100,
        n_jobs: int = 1,
        n_points_iter: int = 1,
        algo_list: Optional[
            List[Union[str, Type[SearchAlgorithm]]]
        ] = None,
        clear=True,
        progress_bar=True,
        use_numba_jit=False,
    ):
        """
        Do optimization for current job.

        Example:

            .. code-block:: python

                from feijoa import create_job
                from feijoa import Experiment
                from feijoa import Real
                from feijoa import SearchSpace


                def objective(experiment: Experiment):
                    x = experiment.params.get("x")
                    y = experiment.params.get("y")
                    return (
                        (1.5 - x + x * y) ** 2
                        + (2.25 - x + x * y**2) ** 2
                        + (2.625 - x + x * y**3) ** 2
                    )


                space = SearchSpace()

                space.insert(Real("x", low=0.0, high=5.0))
                space.insert(Real("y", low=0.0, high=2.0))

                job = create_job(search_space=space)
                job.do(objective, n_trials=50)

        Args:
            objective:
                Objective function.
            n_trials (int):
                Number of total runs.
            n_jobs (int):
                Job's count parallelization with `joblib` backend. if -1 passed => used max of CPU's.
            algo_list (List[Union[str, SearchAlgorithm, Type[SearchAlgorithm]]):
                array of algorithms.
            n_points_iter (int):
                The preferred number of configurations in one epoch. May have no effect for some algorithms.
            clear (bool):
                Clear algo list or not.
            progress_bar (bool):
                Show progress bar (rich) or not.
            use_numba_jit (bool):
                Use numba for objective evaluation speedup.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        # noinspection PyPep8Naming

        if clear:
            cls = type(self.optimizer)
            self.optimizer = cls()

        if (
            algo_list
            or algo_list is None
            and not self.optimizer.algorithms
        ):
            self._load_algo(algo_list)

        if use_numba_jit:
            with ImportWrapper():
                from numba import jit

                objective = jit(objective)

        dela = joblib.delayed(objective)

        progress = (
            Progress(transient=True, disable=not progress_bar)
            if progress_bar
            else contextlib.nullcontext()
        )

        trials = 0
        with progress as bar:  # type: ignore
            task = bar.add_task("Optimizing", total=n_trials)
            while trials < n_trials:
                configurations = self.ask(n_points_iter)

                if not configurations:
                    warnings.warn("No new configurations.")
                    # TODO (qnbhd): make closing
                    break

                configurations = configurations[
                    : min(len(configurations), n_trials)
                ]

                configurations_len = len(configurations)
                trials += configurations_len
                bar.update(task, advance=configurations_len)

                # noinspection PyUnresolvedReferences,PyBroadException
                parallel = joblib.Parallel(
                    n_jobs=n_jobs, prefer="threads"
                )
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    results = parallel(
                        dela(u) for u in configurations
                    )

                # Applying result
                for experiment, result in zip(
                    configurations, results
                ):
                    self.tell(experiment, result)

    def tell(self, experiment, result: Union[float, Result]):
        """
        Finish concrete experiment
        and results to algorithms.

        Args:
            experiment (Experiment):
                Specified experiment.
            result (Union[float, Result]):
                Result for current experiment.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        objective = (
            result.objective_result
            if isinstance(result, Result)
            else result
        )

        if np.isfinite(objective):
            experiment.success_finish()
        else:
            experiment.error_finish()

        if experiment.is_finished():
            self.pending_experiments -= 1

            if isinstance(result, Result):
                self.optimizer.tell(
                    experiment.params, result.objective_result
                )
                experiment.apply(result.objective_result)
                experiment.metrics = result.metrics
            else:
                self.optimizer.tell(experiment.params, result)
                experiment.apply(result)

            self.storage.insert_experiment(experiment)
            return

        raise ExperimentNotFinishedError()

    def _tell_for_loaded(self, experiment: Experiment):
        """
        Tell results for loaded job.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        self.optimizer.tell(
            experiment.params, experiment.objective_result
        )

    def ask(self, n: int) -> Optional[List[Experiment]]:
        """
        Ask for a new experiment.

        Args:
            n (int):
                Preferred count of experiments:

        .. note::
            n may not affect on experiments count.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        configs = self.optimizer.ask(n)

        if not configs:
            return configs

        applicator = partial(
            Experiment,
            job_id=self.id,
            state=ExperimentState.WIP,
        )

        experiments = [
            applicator(
                params=config,
                id=(
                    self.experiments_count
                    + self.pending_experiments
                    + i
                ),
                create_timestamp=datetime.timestamp(datetime.now()),
            )
            for i, config in enumerate(configs)
        ]

        self.pending_experiments += len(experiments)

        return experiments

    def get_dataframe(self, brief=False, desc=False, only_good=False):
        """Make dataframe for current job.

        Args:
            brief (bool):
                Make brief report without additional information.
            desc (bool):
                Fetch only descending by objective function values
                experiments.
            only_good (bool):
                Fetch only correct (state='OK') experiments.

        Returns:
            Pandas dataframe, contains all information
            about optimization session.

        Raises:
            AnyError: If anything bad happens.

        """

        container = []
        m = float("+inf")

        for experiment in self.experiments:
            dataframe_dict = experiment.dict()

            if dataframe_dict["objective_result"] < m:
                m = dataframe_dict["objective_result"]
            else:
                if desc:
                    continue

            dataframe_dict["state"] = str(dataframe_dict["state"])

            if only_good and dataframe_dict["state"] != "OK":
                continue

            params = dataframe_dict.pop("params")

            metrics = dataframe_dict.pop("metrics") or dict()

            dataframe_dict["create_time"] = datetime.fromtimestamp(
                dataframe_dict["create_timestamp"]
            )

            dataframe_dict["finish_time"] = datetime.fromtimestamp(
                dataframe_dict["finish_timestamp"]
            )

            del dataframe_dict["create_timestamp"]
            del dataframe_dict["finish_timestamp"]
            del dataframe_dict["hash"]
            del dataframe_dict["job_id"]

            if brief:
                idx = dataframe_dict["id"]
                objective_result = dataframe_dict["objective_result"]
                container.append(
                    {
                        "id": idx,
                        "objective_result": objective_result,
                        **params,
                    }
                )
                continue

            container.append({**dataframe_dict, **params, **metrics})

        df = pd.DataFrame(container)

        cols_types = {}
        for col in self.search_space.name2param.keys():
            param = self.search_space.get(col)

            if col not in list(df.columns):
                continue

            if isinstance(param, Categorical):
                cols_types[col] = "category"
            elif isinstance(param, Integer):
                cols_types[col] = "int64"
            elif isinstance(param, Real):
                cols_types[col] = "float32"

        df = df.astype(cols_types)

        return df

    @property
    def dataframe(self):
        """Get dataframe property."""

        return self.get_dataframe()

    def add_algorithm(self, algo: SearchAlgorithm):
        """Add algorithm to job's optimizer

        Arguments:
            algo (SearchAlgorithm):
                search algorithm instance.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        self.optimizer.add_algorithm(algo)

    def add_seed(self, seed):
        """Add seed configuration to current job.

        Args:
            seed (dict):
                Seed configuration,
                which must be measured immediately.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        self.seeds.append(seed)


def _load_storage(
    storage_or_name: Union[str, Optional[Storage]]
) -> Storage:
    """
    Load a storage object.

    Args:
        storage_or_name (Union[str, Optional[Storage]]) :
            Storage instance or string with RFC1738 spec.
    """
    if storage_or_name is None:
        return RDBStorage("sqlite:///:memory:")

    if isinstance(storage_or_name, Storage):
        return storage_or_name

    if not isinstance(storage_or_name, str):
        raise InvalidStoragePassed()

    try:
        url = make_url(storage_or_name)
    except ArgumentError:
        raise InvalidStorageRFC1738()

    assert url.database

    if url.drivername == "tinydb":
        with ImportWrapper():
            from feijoa.storages.tiny import TinyDBStorage

            return TinyDBStorage(str(url.database))

    return RDBStorage(storage_or_name)


def create_job(
    *,
    search_space: SearchSpace,
    name: Optional[str] = None,
    storage: Union[str, Optional[Storage]] = None,
    **kwargs,
):
    """Create job instance
    with specified parameters.

    Example:

        .. code-block:: python

            from feijoa import create_job
            from feijoa import SearchSpace

            space = SearchSpace()

            job = create_job(search_space=space)

    Args:
        search_space (SearchSpace):
            Search space instance.
        name (str):
            Name of job.
        storage:
            Storage instance or string
            with `RFC1738` spec.

    Returns:
        Job instance.

    Raises:
        AnyError: If anything bad happens.

    """

    name = name or "job" + datetime.now().strftime(
        "%H_%M_%S_%m_%d_%Y"
    )

    storage = _load_storage(storage)

    assert isinstance(name, str)
    assert isinstance(search_space, SearchSpace)

    if storage.is_job_name_exists(name):
        raise DuplicatedJobError(f"Job {name} is already exists.")

    return Job(
        name, storage, search_space, storage.jobs_count + 1, **kwargs
    )


def load_job(
    *,
    name: str,
    storage: Optional[Union[str, Storage]] = None,
    **kwargs,
):
    """Load existed job instance
    with specified parameters.

    Example:

        .. code-block:: python

            from feijoa import load_job
            from feijoa import SearchSpace

            # job must be in storage

            job = load_job(name="foo", storage="sqlite:///:memory:")

    Args:
        name (str):
            Name of job.
        storage:
            Storage instance or string
            with `RFC1738` spec.

    Returns:
        Job instance.

    Raises:
        AnyError: If anything bad happens.

    """

    storage = _load_storage(storage)

    job_id = storage.get_job_id_by_name(name)

    if not job_id:
        raise JobNotFoundError(f"Job {name} not found is storage.")

    experiments = storage.get_experiments_by_job_id(job_id)
    search_space = storage.get_search_space_by_job_id(job_id)

    job = Job(name, storage, search_space, job_id, **kwargs)

    for experiment in experiments:
        # noinspection PyProtectedMember
        job._tell_for_loaded(experiment)

    return job

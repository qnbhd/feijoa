import logging
import time
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple

from feijoa.utils.imports import ImportWrapper
from feijoa.utils.imports import LazyModuleImportProxy
import numpy as np


with ImportWrapper():
    from pymoo.core.problem import Problem
    from pymoo.core.termination import NoTermination
    from pymoo.core.individual import Individual
    from pymoo.core.population import Population
    from pymoo.algorithms.base.local import LocalSearch

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Real
from feijoa.utils.transformers import inverse_transform
from feijoa.utils.transformers import transform


de = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.de")
ga = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.ga")
cmaes = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.cmaes")
brkga = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.brkga")
direct = LazyModuleImportProxy(
    "pymoo.algorithms.soo.nonconvex.direct"
)
es = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.es")
nichega = LazyModuleImportProxy(
    "pymoo.algorithms.soo.nonconvex.ga_niching"
)
g3pcs = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.g3pcx")
isres = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.isres")
pso = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.pso")
eppso = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.pso_ep")
sres = LazyModuleImportProxy("pymoo.algorithms.soo.nonconvex.sres")


log = logging.getLogger(__name__)


class Genetic(SearchAlgorithm):

    """Genetic algorithms with `pymoo` backend."""

    anchor: str = "GA"
    aliases: Tuple = ("Genetic", "genetic", "GA", "ga")

    algorithm_cls = ga.GA

    def __init__(self, search_space, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.search_space = search_space

        self.bounds = np.zeros((len(self.search_space), 2))

        for i, p in enumerate(self.search_space):
            if isinstance(p, (Integer, Real)):
                self.bounds[i, :] = np.array([p.low, p.high])
            if isinstance(p, Categorical):
                self.bounds[i, :] = np.array([0, len(p.choices) - 1])

        self.xl = self.bounds[:, 0]
        self.xu = self.bounds[:, 1]

        self._ask_gen = None

        self.problem = Problem(
            n_var=len(self.search_space),
            n_obj=1,
            n_constr=0,
            xl=self.xl,
            xu=self.xu,
        )

        self.algorithm = self.algorithm_cls(**kwargs)

        # let the algorithm object never terminate and let the loop control it
        self.termination = NoTermination()

        # create an algorithm object that never terminates
        self.algorithm.setup(
            self.problem, termination=self.termination
        )

        self.args = args
        self.kwargs = kwargs

        self.algorithm.start_time = time.time()

        # fix the random seed manually
        np.random.seed(0)

        self.pool = []

        self.pop = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self._ask_gen:
            self._ask_gen = self._ask(n)
            log.debug(
                "Parameter `n` does not affect on configuration's count,"
                f" because {self.__class__.__name__} is can have variable pop size."
            )
        return next(self._ask_gen)

    def _ask(self, n: int) -> Generator:
        n_gen = 0

        while True:
            self.pop = self.algorithm.ask()

            # get the design space values of the algorithm
            X = self.pop.get("X")

            log.debug(f"Generation: {n_gen} for {self.name}")

            configs = [
                Configuration(
                    transform(
                        solution,
                        self.search_space,
                    ),
                    requestor=self.name,
                    request_id=i,
                )
                for i, (individual, solution) in enumerate(
                    zip(self.pop, X)
                )
            ]

            yield configs

            self.algorithm.tell(infills=self.pop)

            n_gen += 1

    def tell(self, config, result):

        # take our results

        if config.requestor == self.name:
            self.pop[config.request_id].F = np.array([result])
            self.pool.append(self.pop[config.request_id])
            return

        # take experience from other algorithms

        x0 = Individual()

        # cook our individual instance
        x0.X = inverse_transform(config, self.search_space)
        x0.F = np.array([result])

        if (
            self.pool
            and result
            < min(self.pool, key=lambda solution: solution.F).F
        ):
            log.debug(f"Restarting {self.name}")

            # take into account base class type
            params = {
                "sampling": Population(
                    individuals=np.array(self.pool)
                )
            }
            if issubclass(self.algorithm_cls, LocalSearch):
                params = {
                    "x0": Population(individuals=np.array(self.pool))
                }

            # restart our algorithm
            self.algorithm = self.algorithm_cls(
                *self.args, **self.kwargs, **params
            )
            self.algorithm.setup(
                self.problem, termination=self.termination
            )

        self.pool.append(x0)


class DifferentialEvolution(Genetic):
    @property
    def algorithm_cls(self):
        return de.DE

    anchor = "de"
    aliases = ("differentialevolution", "DE")


class CMAES(Genetic):
    @property
    def algorithm_cls(self):
        return cmaes.CMAES

    anchor = "cmaes"
    aliases = ("cmaes",)


class BRKGA(Genetic):
    @property
    def algorithm_cls(self):
        return brkga.BRKGA

    anchor = "brkga"
    aliases = ("brkga",)


class DIRECT(Genetic):
    @property
    def algorithm_cls(self):
        return direct.DIRECT

    anchor = "direct"
    aliases = ("direct",)


class ES(Genetic):
    @property
    def algorithm_cls(self):
        return es.ES

    anchor = "es"
    aliases = ("es",)


class G3PCX(Genetic):
    @property
    def algorithm_cls(self):
        return g3pcs.G3PCX

    anchor = "g3pcx"
    aliases = ("g3pcx",)


class NICHEGA(Genetic):
    @property
    def algorithm_cls(self):
        return nichega.NicheGA

    anchor = "nichega"
    aliases = ("niche", "nichega")


class PSO(Genetic):
    @property
    def algorithm_cls(self):
        return pso.PSO

    anchor = "pso"
    aliases = ("pso",)


class EPPSO(Genetic):
    @property
    def algorithm_cls(self):
        return eppso.EPPSO

    anchor = "eppso"
    aliases = ("eppso",)


class SRES(Genetic):
    @property
    def algorithm_cls(self):
        return sres.SRES

    anchor = "sres"
    aliases = ("sres",)


class ISRES(Genetic):
    @property
    def algorithm_cls(self):
        return isres.ISRES

    anchor = "isres"
    aliases = ("isres",)

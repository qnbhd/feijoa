import logging
from typing import Generator
from typing import List
from typing import Optional

from bayesmark.builtin_opt.hyperopt_optimizer import HyperoptOptimizer
from bayesmark.builtin_opt.opentuner_optimizer import (
    OpentunerOptimizer,
)
from bayesmark.builtin_opt.pysot_optimizer import PySOTOptimizer

from feijoa.models.configuration import Configuration
from feijoa.search.oracles.oracle import Oracle
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Real


log = logging.getLogger(__name__)


mapper = {
    Integer: "int",
    Real: "real",
    Categorical: "cat",
}


def cook_api_config(space):
    cfg = {}
    for param in space:
        kind = mapper[type(param)]
        s = "linear"

        pp = {
            "type": kind,
            "space": s,
        }

        if isinstance(param, (Integer, Real)):
            ran = (param.low, param.high)
            pp["range"] = ran
        if isinstance(param, Categorical):
            values = param.choices
            pp["values"] = values

        cfg[param.name] = pp

    return cfg


class BayesmarkAdapterHyperOpt(Oracle):

    OPTIMIZER = HyperoptOptimizer

    anchor = "bm_hyper"
    aliases = (
        "hyperopt",
        "bayesmark-hyperopt",
    )

    def __init__(self, search_space, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.space = search_space
        self.name = f"Optuna<{self.OPTIMIZER.__name__}>"

        api_cfg = cook_api_config(self.space)
        self.optimizer = self.OPTIMIZER(api_cfg)
        self._ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self._ask_gen:
            self._ask_gen = self._ask(n)
        return next(self._ask_gen)

    def _ask(self, n: int = 1) -> Generator:

        while True:
            cfgs = self.optimizer.suggest(n)
            log.info(f"{cfgs}")
            prepared = self.make_configs(cfgs)
            yield prepared

    def tell(self, config, result):
        self.optimizer.observe([config], [float(result)])

    def make_configs(self, configs):
        configurations = list()
        for c in configs:
            configurations.append(
                Configuration(
                    c,
                    requestor=self.name,
                )
            )
        return configurations


class BayesmarkOpentuner(BayesmarkAdapterHyperOpt):
    OPTIMIZER = OpentunerOptimizer

    anchor = "bm_opentuner"
    aliases = (
        "opentuner",
        "bayesmark-opentuner",
    )


class BayesmarkPYSOT(BayesmarkAdapterHyperOpt):
    OPTIMIZER = PySOTOptimizer

    anchor = "bm_pysot"
    aliases = (
        "pysot",
        "bayesmark-pysot",
    )


# class BayesmarkNevergrad(BayesmarkAdapterHyperOpt):
#     OPTIMIZER = NevergradOptimizer
#
#     anchor = "bm_nevergrad"
#     aliases = (
#         "nevergrad",
#         "bayesmark-nevergrad",
#     )

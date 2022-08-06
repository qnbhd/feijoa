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
"""Importances plot module."""

import numpy as np
import plotly.graph_objs as go

from feijoa import Categorical
from feijoa import create_job
from feijoa import Real
from feijoa import SearchSpace
from feijoa.importance.mdi import MDIEvaluator
from feijoa.importance.rsfanova_boosted import RsFanovaEvaluator


def plot_importances(
    job,
    fig=None,
):
    """Plot the importances for
    a specified job.

    Args:
        job (Job):
            Job instance.
        fig (go.Figure):
            Plotly figure object.

    Raises:
        AnyError: If anything bad happens.

    """

    fig = fig or go.Figure()

    importance_evaluator = MDIEvaluator()
    evaluated = importance_evaluator.do(job)
    params, mdi_importance = (
        evaluated["parameters"],
        evaluated["importance"],
    )
    rsfanova_evaluator = RsFanovaEvaluator()
    rsfanova_importance = rsfanova_evaluator.do(job)["importance"]
    importance = mdi_importance + rsfanova_importance
    importance = importance / 2

    fig.add_bar(
        x=params,
        y=importance,
    )

    fig.update_layout(
        title="Parameters importance plot",
        xaxis_title="Parameter",
        yaxis_title="Relative Importance",
        xaxis={"categoryorder": "total descending"},
    )

    return fig


def objective(experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    z = experiment.params.get("z")
    w = experiment.params.get("w")
    u = experiment.params.get("u")

    ob = x + np.sqrt(y) + np.log(z) + 10 * w
    ob += -10 if u == "bar" else 0
    # ob = x + np.sqrt(y)
    return ob


def main():
    space = SearchSpace()

    space.insert(Real("x", low=0.1, high=3.0))
    space.insert(Real("y", low=0.1, high=3.0))
    space.insert(Real("z", low=0.1, high=3.0))
    space.insert(Real("w", low=0.0, high=3.0))
    space.insert(Categorical("u", choices=["foo", "bar"]))

    job = create_job(search_space=space)
    job.do(
        objective,
        n_jobs=-1,
        n_trials=100,
        algo_list=["bayesian"],
        progress_bar=True,
        use_numba_jit=True,
    )

    fig = plot_importances(job)
    fig.show()


if __name__ == "__main__":
    main()

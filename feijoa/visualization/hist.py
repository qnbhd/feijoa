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
"""Histogram's plot module."""

import plotly.graph_objs as go

from feijoa import create_job
from feijoa import Real
from feijoa import SearchSpace


def plot_objective_hist(
    job,
    fig=None,
):
    """Plot objective hists for
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
    df = job.get_dataframe(brief=True)

    fig.add_histogram(x=df["objective_result"], nbinsx=100)

    fig.update_layout(
        title="Objective result histogram",
        xaxis_title="Objective value",
        yaxis_title="Count",
    )

    return fig


def objective(experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    return (
        (1.5 - x + x * y) ** 2
        + (2.25 - x + x * y**2) ** 2
        + (2.625 - x + x * y**3) ** 2
    )


def main():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=3.0))
    space.insert(Real("y", low=0.0, high=1.0))

    job = create_job(search_space=space)
    job.do(
        objective,
        n_jobs=-1,
        n_trials=2000,
        algo_list=["grid"],
        progress_bar=True,
        use_numba_jit=True,
    )

    fig = plot_objective_hist(job)
    fig.show()


if __name__ == "__main__":
    main()

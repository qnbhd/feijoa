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
from feijoa import create_job
from feijoa import Real
from feijoa import SearchSpace
import numpy as np
import plotly.graph_objs as go


def plot_edf(
    job,
    fig=None,
    name=None,
):
    name = name or job.name
    fig = fig or go.Figure()
    df = job.get_dataframe(brief=True)
    objectives = df["objective_result"]
    min_value, max_value = objectives.min(), objectives.max()
    lspace = np.linspace(min_value, max_value, 100)

    dist = np.array([np.sum(objectives <= x) for x in lspace]) / len(
        objectives
    )

    fig.add_trace(
        go.Scatter(
            x=lspace,
            y=dist,
            mode="lines",
            name=f"{name}",
        )
    )

    fig.update_layout(
        title="Empirical distribution plot",
        xaxis_title="Objective value",
        yaxis_title="Cumulative probability",
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
        n_proc=-1,
        n_trials=2000,
        algo_list=["grid"],
        progress_bar=True,
        use_numba_jit=True,
    )

    fig = plot_edf(job)
    fig.show()


if __name__ == "__main__":
    main()

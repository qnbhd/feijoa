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
"""Optimization history plot module."""

import plotly.graph_objs as go


def plot_optimization_history(
    job,
    mode="lines+markers",
    name=None,
    fig=None,
    only_best=True,
    invert_objective=False,
):
    """
    Plot optimization history.

    Args:
        job (Job):
            Job instance.
        mode (str):
            Plotly plot mode. Defaults to "lines+markers"
        name (str):
            Name of trace.
        fig (go.Figure):
            Plotly figure object.
        only_best:
            Plotly only bests results.
            (Descending sequence by objective values)
        invert_objective (bool):
            For the maximization task, it is
            necessary to invert the value of
            the view function, in this case,
            you must check this box to get
            corrective values


    Raises:
        AnyError: If anything bad happens.

    """

    df = job.get_dataframe(desc=True)
    obj = df["objective_result"] * (1 if not invert_objective else -1)
    iterations = df["id"]
    name = name or job.name

    fig = fig or go.Figure()

    fig.add_trace(
        go.Scatter(
            x=iterations,
            y=obj,
            mode=mode,
            name=f"{name} bests",
        )
    )

    if not only_best:
        full_df = job.get_dataframe()
        fig.add_trace(
            go.Scatter(
                x=full_df["id"],
                y=full_df["objective_result"],
                mode="markers",
                name=name,
            )
        )

    fig.update_layout(
        title="Optimization history plot",
        xaxis_title="Iteration",
        yaxis_title="Objective value",
    )

    return fig


def plot_compare_jobs(
    *jobs,
    mode="lines+markers",
    fig=None,
    names=None,
    invert_objective=False,
):
    """
    Plot comparison between jobs.

    Args:
        jobs (List[Job]):
            List of jobs.
        mode (str):
            Plotly plot mode. Defaults to "lines+markers"
        names (List[str]):
            Names of traces.
        fig (go.Figure):
            Plotly figure object.
        invert_objective (bool):
            For the maximization task, it is
            necessary to invert the value of
            the view function, in this case,
            you must check this box to get
            corrective values

    Raises:
        AnyError: If anything bad happens.

    """

    if isinstance(names, list) and len(names) != len(jobs):
        raise ValueError(f"Names must contains {len(jobs)} values.")

    names = names or [job.name for job in jobs]
    print(names)

    fig = fig or go.Figure()

    for job, name in zip(jobs, names):
        plot_optimization_history(job, mode, name, fig)

    return fig

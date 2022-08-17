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
"""EDF plot module."""

import numpy as np
import plotly.graph_objs as go


__all__ = ["plot_edf"]


def plot_edf(
    job,
    fig=None,
    name=None,
    invert_objective=False,
):
    """
    Plot the EDF of a job.

    Args:
        job (Job):
            Job instance.
        fig (go.Figure):
            Plotly figure object.
        name:
            Name of trace.
        invert_objective (bool):
            For the maximization task, it is
            necessary to invert the value of
            the view function, in this case,
            you must check this box to get
            corrective values

    Raises:
        AnyError: If anything bad happens.

    """

    name = name or job.name
    fig = fig or go.Figure()
    df = job.get_dataframe(brief=True)
    objectives = df["objective_result"] * (
        1 if not invert_objective else -1
    )
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

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


def plot_objective_hist(
    job,
    fig=None,
    invert_objective=False,
):
    """
    Plot objective hists for
    a specified job.

    Args:
        job (Job):
            Job instance.
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

    fig = fig or go.Figure()
    df = job.get_dataframe(brief=True)
    objectives = df["objective_result"] * (
        1 if not invert_objective else -1
    )

    fig.add_histogram(x=objectives, nbinsx=100)

    fig.update_layout(
        title="Objective result histogram",
        xaxis_title="Objective value",
        yaxis_title="Count",
    )

    return fig

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
"""Evaluations plot module."""

import plotly.graph_objs as go
from plotly.subplots import make_subplots


def pad(string: str, width: int, filler=" ", fill_chars=3):
    """
    Pads a string to a given width.

    Args:
        string (str):
            String instance.
        width (int):
            Target width of string.
        filler:
            Fill places with specified char.
        fill_chars:
            Count of chars to fill.

    Raises:
        AnyError: If anything bad happens.

    """

    if len(string) <= width:
        return string
    return f"{string[:width - 3]}{filler * fill_chars}"


def plot_evaluations(job, params=None, invert_objective=False):
    """
    Plot evaluations of job.

    Args:
        job (Job):
            Job instance.
        params (list):
            List of parameters to plot.
        invert_objective (bool):
            For the maximization task, it is
            necessary to invert the value of
            the view function, in this case,
            you must check this box to get
            corrective values

    Raises:
        AnyError: If anything bad happens.

    """

    df = job.get_dataframe(brief=True, only_good=True)
    objectives = df["objective_result"] * (
        1 if not invert_objective else -1
    )
    df.drop(columns=["id", "objective_result"], inplace=True)
    params = params or df.columns

    if any([param not in df.columns for param in params]):
        raise ValueError("Unknown columns in specified job.")

    params_length = len(params)

    fig = make_subplots(rows=params_length, cols=params_length)

    for i, col_x in enumerate(params):
        for j, col_y in enumerate(params):
            if i > j:
                continue

            if i == j:
                fig.add_histogram(
                    x=df[col_x],
                    nbinsx=30,
                    row=i + 1,
                    col=i + 1,
                    marker=dict(
                        color="#330C73",
                    ),
                    opacity=0.75,
                )
                continue

            x = df[col_x]
            y = df[col_y]

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    marker=dict(
                        color=objectives,
                        colorscale="TealRose_r",
                        symbol="circle",
                        colorbar=dict(title="Objective result"),
                        line=dict(width=1, color="black"),
                    ),
                ),
                col=i + 1,
                row=j + 1,
            )

    fig.update_layout(
        title="Evaluations plot",
        showlegend=False,
        bargap=0.2,
        bargroupgap=0.1,
    )

    def cut(base, num):
        if num == 1:
            return base
        return base if num == 1 else f"{base}{num}"

    positions = [
        (
            *fig["layout"][cut("xaxis", i)]["domain"],
            *fig["layout"][cut("yaxis", i)]["domain"],
        )
        for i in range(1, params_length**2 + 1)
    ]

    positions = [
        (x0, x1, y0, y1)
        for (x0, x1, y0, y1) in positions
        if x0 == 0.0 or y0 == 0.0
    ]

    names = list(params) * 2

    for i, (x0, x1, y0, y1) in enumerate(positions):
        x = x0
        y = y0
        angle = 0

        if x == 0.0:
            x -= 0.05
            y = (y0 + y1) / 2
            angle = 270
        else:
            x = (x0 + x1) / 2 + 0.02
            y -= 0.08

        fig.add_annotation(
            dict(
                x=x,
                y=y,
                xref="paper",
                yref="paper",
                text=pad(names.pop(0), 10, filler="."),
                showarrow=False,
            ),
            textangle=angle,
        )

        if x0 == 0 and y0 == 0:
            x_ = (x0 + x1) / 2
            y_ = -0.08
            angle = 0
            fig.add_annotation(
                dict(
                    x=x_,
                    y=y_,
                    xref="paper",
                    yref="paper",
                    text=pad(names.pop(0), 10, filler="."),
                    showarrow=False,
                ),
                textangle=angle,
            )

    return fig

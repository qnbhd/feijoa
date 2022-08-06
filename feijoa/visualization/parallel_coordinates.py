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
import logging

import numpy as np
import plotly.graph_objs as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

from feijoa import Categorical
from feijoa import create_job
from feijoa import Integer
from feijoa import Real
from feijoa import SearchSpace
from feijoa.search.algorithms.bayesian import BayesianAlgorithm


def pad(string: str, width: int, filler=" ", fill_chars=3):
    """Pads a string to a given width.

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


def plot_parallel_coordinates(
    job,
    params=None,
):
    """Plot the parallel coordinates for
    a specified job.

    Args:
        job (Job):
            Job instance.
        params (list):
            Parameters names to plot.

    Raises:
        AnyError: If anything bad happens.

    """

    df = job.get_dataframe(brief=True, only_good=True)
    objectives = df["objective_result"]
    df.drop(columns=["id", "objective_result"], inplace=True)
    omin = objectives.min()
    omax = objectives.max()
    params = params or df.columns

    if any([param not in df.columns for param in params]):
        raise ValueError("Unknown columns in specified job.")

    dimensions = [
        {
            "label": "objective_result",
            "values": objectives,
            "range": (omin, omax),
        }
    ]

    if any([df[col].dtype.name == "object" for col in params]):
        raise ValueError(
            "Dataframe should not have columns with object type."
        )

    for col in sorted(params, reverse=True):
        dim = {
            "label": pad(col, 15, "."),
        }

        if df[col].dtype.name == "category":
            ticks = LabelEncoder().fit_transform(df[col])
            ticks_text = df[col]

            dim["values"] = ticks
            dim["tickvals"] = np.arange(len(set(ticks)))
            dim["ticktext"] = ticks_text
            dim["range"] = ticks.min(), ticks.max()
        else:
            dim["values"] = df[col]
            dim["range"] = df[col].min(), df[col].max()

        dimensions.append(dim)

    tr = [
        go.Parcoords(
            dimensions=dimensions,
            line=dict(
                color=objectives,
                colorscale="TealRose",
                colorbar=dict(title="objective_result"),
                showscale=True,
            ),
        )
    ]

    layout = go.Layout(title="Parallel Coordinate Plot")
    fig = go.Figure(data=tr, layout=layout)
    return fig


def objective(experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    z = experiment.params.get("z")
    w = experiment.params.get("w")

    u = (
        (1.5 - x + x * y) ** 2
        + (2.25 - x + x * y**2) ** 2
        + (2.625 - x + x * y**3) ** 2
    )

    u += 1 if z == "foo" else -1
    u -= w
    return u


def main():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=3.0))
    space.insert(Real("y", low=0.0, high=1.0))
    space.insert(Categorical("z", choices=["foo", "bar"]))
    space.insert(Integer("w", low=0, high=4))

    ba = BayesianAlgorithm(
        search_space=space, regressor=RandomForestRegressor(n_jobs=-1)
    )

    job = create_job(search_space=space)
    logging.basicConfig(level="DEBUG")
    job.do(
        objective,
        n_jobs=-1,
        n_trials=50,
        algo_list=[ba],
        progress_bar=True,
        use_numba_jit=True,
    )
    fig = plot_parallel_coordinates(job, params=["x", "y", "w"])
    fig.show()


if __name__ == "__main__":
    main()

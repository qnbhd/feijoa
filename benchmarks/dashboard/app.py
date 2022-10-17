from collections import defaultdict
from contextlib import suppress
from itertools import chain
from typing import List

import callbacks
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ujson
from dash import Input, Output, State

from benchmarks.calculations import calculate_general_ranks
from benchmarks.dashboard.dash_mixin import DashMixin, dashed
from benchmarks.dashboard.layouts.span import pickup_span_layout
from benchmarks.dashboard.utils import parse_metrics_and_directions
from benchmarks.ranker import feijoa_score
from benchmarks.storage import BenchmarksStorage, Problem

# the style arguments for the sidebar. We use position:fixed and a fixed width
from feijoa.utils.logging import init


class Dashboard(DashMixin):
    def __init__(self, storage_url, *args, **kwargs):
        super().__init__(*args)

        self.storage = BenchmarksStorage(storage_url)

        self.app.layout = pickup_span_layout()

    def run(self, *args, **kwargs):
        self.app.run_server(*args, **kwargs)

    @dashed(
        Output("problems_dropdown", "options"),
        Input("interval-component-dropdown", "n_intervals"),
    )
    def update_dropdown(self, _):
        problems = self.storage.get_unique_problems()

        drops = [
            {"label": p.capitalize(), "value": p} for p in chain(problems, ["all"])
        ]
        return drops

    @dashed(
        Output("live-update-graph", "figure"),
        State("live-update-graph", "figure"),
        Input("interval-component", "n_intervals"),
        Input("selected-features", "data"),
        Input("problem-name", "data"),
        Input("yaxis-scale", "data"),
        Input("directions", "data"),
        Input("theme", "data"),
    )
    def update_graph_live(
        self,
        fig,
        n,
        features,
        problem,
        yaxis_scale,
        directions,
        theme,
    ):

        theme = ujson.loads(theme)
        theme = "plotly_dark" if theme == "dark" else "plotly_white"

        features: List[str] = ujson.loads(features)
        problem = ujson.loads(problem)
        yaxis_scale = ujson.loads(yaxis_scale)

        trials = self.storage.fetch_trials(
            (lambda x: x.filter(Problem.name == problem))
            if problem != "all"
            else lambda x: x
        )

        dataframe = pd.DataFrame.from_dict(trials)

        if dataframe.empty:
            return go.Figure()

        metrics, directions = parse_metrics_and_directions(
            features, ujson.loads(directions)
        )

        ranks = calculate_general_ranks(dataframe, problem, features, directions)

        with suppress(ValueError):
            fig = px.bar(
                y=ranks["optimizer"],
                x=ranks["rank"],
                color_discrete_sequence=px.colors.sequential.Turbo,
                color=ranks["rank"],
                orientation="h",
            )

        fig.update_layout(
            title="Score",
            yaxis=dict(
                title="Oracle",
                categoryorder="total ascending",
            ),
            autosize=True,
            xaxis=dict(
                title="Rank",
                type=yaxis_scale,
                tickformat=".5f",
            ),
            barmode="stack",
            bargroupgap=0.1,
            bargap=0.1,
            hovermode="closest",
            template=theme,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig

    @dashed(
        Output("live-update-graph1", "figure"),
        Output("live-update-graph-polar", "figure"),
        Input("problem-name", "data"),
        Input("coefficients", "data"),
        Input("theme", "data"),
    )
    def update_graph_live_1(self, problem, coefficients, theme):
        problem = ujson.loads(problem)
        coefficients = ujson.loads(coefficients)

        theme = ujson.loads(theme)
        theme = "plotly_dark" if theme == "dark" else "plotly_white"

        trials = self.storage.fetch_results(
            lambda x: x.filter(Problem.name == problem),
        )

        df = pd.DataFrame.from_dict(trials)

        fig = go.Figure()
        fig_2 = go.Figure()

        if df.empty:
            return fig, fig_2

        points_dict = defaultdict(list)

        for index, row in df.iterrows():
            points_dict[row["optimizer"]].append(
                [row["id_in_trial"], row["objective_value"]]
            )

        optimizers = []
        deltas_opt_mean = []
        deltas_opt_med = []
        convergence_2 = []

        results = list()
        iterations = list()

        # convergence = np.zeros_like(df["objective_result"])
        for opt, indices_and_points in points_dict.items():
            convergence = []
            convergence_2 = []

            m = float("+inf")
            indices = []
            optimizers.append(opt)
            deltas = []
            for index, point in indices_and_points:

                if point < m:
                    convergence.append(point)
                    indices.append(index)
                    if np.isfinite(m):
                        deltas.append(m - point)
                    m = point

                convergence_2.append(m)

            results.append(convergence)
            iterations.append(indices)

            fig.add_scatter(
                x=list(range(len(convergence_2))),
                y=convergence_2,
                mode="lines",
                name=opt,
            )
            deltas_opt_mean.append(np.array(deltas).mean())
            deltas_opt_med.append(np.median(deltas))

        scores = feijoa_score(
            coefficients["alpha"],
            coefficients["beta"],
            coefficients["gamma"],
            optimizers,
            results,
            iterations,
        )

        # fig_2.add_bar(x=optimizers, y=deltas_opt_mean, name='mean')
        # fig_2.add_bar(x=optimizers, y=deltas_opt_med, name='median')
        fig_2.add_bar(
            x=list(scores.keys()),
            y=list(scores.values()),
            name="feijoa ranks",
        )

        fig.update_traces(line=dict(width=2))
        fig.update_layout(
            title="Convergence plot",
            xaxis=dict(
                title="Oracle",
            ),
            autosize=True,
            yaxis=dict(
                title="Rank",
            ),
            barmode="stack",
            bargroupgap=0.1,
            bargap=0.1,
            hovermode="closest",
            template=theme,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            # legend=dict(yanchor="bottom", y=0, xanchor="left", x=0.4)
        )

        fig_2.update_layout(
            title="Convergence rate",
            xaxis=dict(
                title="Oracle",
                categoryorder="total descending",
            ),
            autosize=True,
            yaxis=dict(
                title="Rank",
                categoryorder="total descending",
            ),
            barmode="group",
            bargroupgap=0.1,
            bargap=0.1,
            hovermode="closest",
            template=theme,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            # legend=dict(yanchor="bottom", y=0, xanchor="left", x=0.4)
        )

        return fig, fig_2


if __name__ == "__main__":
    init()
    board = Dashboard(
        "sqlite:///test.db?check_same_thread=False",
        callbacks.clientside,
        callbacks.ui,
        callbacks.shared,
    )
    board.run()

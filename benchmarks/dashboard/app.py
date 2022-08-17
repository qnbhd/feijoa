import os

from benchmarks.dashboard.dash_mixin import dashed
from benchmarks.dashboard.dash_mixin import DashMixin
from benchmarks.simplified_suite import BenchmarkSuite
from benchmarks.trials import BenchesStorage
from dash.dependencies import Input
from dash.dependencies import Output
import pandas as pd
from paretoset import paretorank
import plotly.graph_objs as go
import ujson


pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", lambda x: "%.5f" % x)


class Dashboard(DashMixin):
    def __init__(self, storage_url):
        super().__init__()

        self.storage = BenchesStorage(
            "postgresql+psycopg2://postgres:myPassword@188.124.39.245/postgres"
        )

    def run(self, *args, **kwargs):
        self.app.run_server(*args, **kwargs)

    @dashed(
        Output("problems_dropdown", "options"),
        Input("interval-component-dropdown", "n_intervals"),
    )
    def update_dropdown(self, *args, **kwargs):
        problems = self.storage.get_unique_problems()

        drops = [
            {"label": p.capitalize(), "value": p}
            for p in [*problems, "all"]
        ]
        return drops

    @dashed(
        Output("problem-name", "data"),
        Input("problems_dropdown", "value"),
    )
    def set_display_children(self, selected_value):
        return ujson.dumps(selected_value)

    @dashed(
        Output("selected-features", "data"),
        Input("directions-checklist", "value"),
    )
    def update_features(self, value):
        return ujson.dumps(value)

    @dashed(
        Output("live-update-graph", "figure"),
        Input("interval-component", "n_intervals"),
        Input("selected-features", "data"),
        Input("problem-name", "data"),
    )
    def update_graph_live(self, n, features, problem):
        fig = go.Figure()

        features = ujson.loads(features)
        problem = ujson.loads(problem)

        trials = self.storage.load_trials(
            problem if problem != "all" else None
        )
        dataframe = pd.DataFrame.from_dict(trials)

        dataframe = BenchmarkSuite.calculate_pareto_ranking(
            dataframe, problem, features
        )

        dataframe.sort_values(
            by="rank", inplace=True, ascending=False
        )

        fig.add_bar(
            x=dataframe["optimizer"],
            y=dataframe["rank"],
            marker_color="#5F9D00",
        )

        fig.update_layout(
            title="Score",
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
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig


if __name__ == "__main__":
    # features = ['best', 'time']
    #
    # storage = BenchesStorage(
    #     'postgresql+psycopg2://postgres:myPassword@188.124.39.245/postgres'
    # )
    #
    # trials = storage.load_trials(
    # dataframe = pd.DataFrame.from_dict(trials)
    #
    # dataframe = BenchmarkSuite.calculate_pareto_ranking(dataframe, problem, features)
    #
    # dataframe.sort_values(by='rank', inplace=True, ascending=False)
    board = Dashboard("woo")
    board.run(threaded=True)

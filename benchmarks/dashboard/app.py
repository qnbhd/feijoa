import os

import ujson
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

from benchmarks.dashboard.dash_mixin import DashMixin, dashed
from benchmarks.trials import BenchesStorage
from paretoset import paretorank


pd.set_option("display.max_colwidth", None)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


class Dashboard(DashMixin):

    def __init__(self, storage_url):
        super().__init__()

        self.storage = BenchesStorage(
            'postgresql+psycopg2://postgres:myPassword@188.124.39.245/postgres'
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
            {
                'label': p.capitalize(),
                'value': p
            }
            for p in problems
        ]
        return drops

    @dashed(
        Output('problem-name', 'data'),
        Input('problems_dropdown', 'value'),
    )
    def set_display_children(self, selected_value):
        return ujson.dumps(selected_value)

    @dashed(
        Output('selected-features', 'data'),
        Input('directions-checklist', 'value'),
    )
    def update_features(self, value):
        return ujson.dumps(value)

    @dashed(
        Output("live-update-graph", "figure"),
        Input('selected-features', 'data'),
        Input('problem-name', 'data'),
    )
    def update_graph_live(self, features, problem):
        fig = go.Figure()

        directions = []
        metrics = []

        features = ujson.loads(features)
        problem = ujson.loads(problem)

        for feature in features:
            metric, direction = feature.split(':')
            directions.append(direction)
            metrics.append(metric)

        trials = self.storage.load_trials(problem)
        dataframe = pd.DataFrame.from_dict(trials)

        dataframe.drop(columns=['pareto_ranking'], inplace=True)
        problem_df = dataframe[metrics]
        ranks = paretorank(
            problem_df, sense=directions
        )

        dataframe['rank'] = [1/rank for rank in ranks]

        dataframe.sort_values(by='rank', inplace=True, ascending=False)

        fig.add_bar(x=dataframe["optimizer"], y=dataframe["rank"], marker_color='#5F9D00')

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


if __name__ == '__main__':
    board = Dashboard('woo')
    board.run(debug=True, threaded=True)

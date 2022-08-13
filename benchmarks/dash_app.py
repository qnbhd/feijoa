import datetime

from benchmarks.trials import BenchesStorage
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
import dash_daq as daq
import plotly.graph_objs as go


external_stylesheets = ["/assets/stylesheet.css"]


dark_theme = {
    "main-background": "black",
    "header-text": "white",
    "sub-text": "white",
}

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_external_path="/assets/",
)

rootLayout = html.Div(
    html.Div(
        [
            html.H4(
                "Feijoa oracle' ranking",
                style={"color": dark_theme["header-text"]},
            ),
            dcc.Graph(id="live-update-graph"),
            dcc.Interval(
                id="interval-component",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
            ),
        ]
    )
)

app.layout = app.layout = html.Div(
    id="dark-theme-container",
    children=[
        html.Br(),
        html.Div(
            id="dark-theme-components-1",
            children=[
                daq.DarkThemeProvider(
                    theme=dark_theme, children=rootLayout
                )
            ],
        ),
    ],
    style={"padding": "50px"},
)


# Multiple components can update everytime interval gets fired.
@app.callback(
    Output("live-update-graph", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_graph_live(n):
    fig = go.Figure()
    storage = BenchesStorage("postgresql+psycopg2://postgres:myPassword@188.124.39.245/postgres")
    ranking = storage.get_total_ranking()

    fig.add_bar(x=ranking["optimizer"], y=ranking["ranking"])

    fig.update_layout(
        title="Objective result histogram",
        xaxis_title="Objective value",
        yaxis_title="Count",
        barmode="stack",
        bargroupgap=0.1,
        bargap=0.1,
        hovermode="closest",
        transition={"duration": 300, "easing": "cubic-in-out"},
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


if __name__ == "__main__":
    app.run_server(
        debug=True, threaded=True, dev_tools_hot_reload_interval=300
    )

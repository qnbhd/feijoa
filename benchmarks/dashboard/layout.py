from dash import dash_table
from dash import dcc
from dash import html


def make_layout(app):
    layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Img(
                                                src=app.get_asset_url(
                                                    "feijoa-logo.svg"
                                                ),
                                                style={
                                                    "height": "100px",
                                                },
                                            ),
                                            html.H4(
                                                "Oracles ranking"
                                            ),
                                        ],
                                        className="header__title",
                                    ),
                                    html.Div(
                                        [
                                            html.P(
                                                "See oracles ranking in realtime."
                                            )
                                        ],
                                        className="header__info pb-20",
                                    ),
                                    html.Div(
                                        [
                                            html.A(
                                                "View on GitHub",
                                                href="https://github.com/qnbhd/feijoa",
                                                target="_blank",
                                            )
                                        ],
                                        className="header__button",
                                    ),
                                ],
                                className="header pb-20",
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="live-update-graph",
                                        style={"width": "100%"}
                                    ),
                                    dcc.Interval(
                                        id="interval-component",
                                        interval=2 * 1000,  # in milliseconds
                                        n_intervals=0,
                                    ),
                                    html.P(
                                        id="placeholder-graph",
                                        style={"display": "none"},
                                    ),
                                ],

                                className="graph__container",
                            ),
                            html.Div(
                                [
                                    dash_table.DataTable(
                                        id="live-update-dataframe",
                                        style_data={
                                            "backgroundColor": "black",
                                            "color": "white",
                                        },
                                    ),
                                ],
                                className="table__container",
                            ),
                        ],
                        className="container",
                    )
                ],
                className="two-thirds column app__left__section",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "Select problem",
                                className="subheader",
                            ),
                            html.Span("  |  "),
                            html.Span(
                                "Select existed problem for analysis.",
                                className="small-text",
                            ),
                        ],
                        className="pb-20",
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="problems_dropdown",
                                options=[],
                                value="rosen",
                                placeholder="Select problem",
                                style=dict(
                                    width="100%",
                                    display="inline-block",
                                    verticalAlign="middle",
                                    borderRadius=0,
                                    borderStyle=None,
                                    backgroundColor="#161616",
                                ),
                                className="dropdown",
                            ),
                            html.P(
                                id="placeholder-1",
                                style={"display": "none"},
                            ),
                            dcc.Interval(
                                id="interval-component-dropdown",
                                interval=1 * 1000,  # in milliseconds
                                n_intervals=0,
                            ),
                            html.Br(),
                            html.Br(),
                            html.Div(
                                [
                                    html.Span(
                                        "Select metrics",
                                        className="subheader",
                                    ),
                                    html.Span("  |  "),
                                    html.Span(
                                        "Select metrics for analysis.",
                                        className="small-text",
                                    ),
                                ],
                                className="pb-20",
                            ),
                            dcc.Checklist(
                                options=[
                                    {
                                        "label": "Time",
                                        "value": "time:min",
                                    },
                                    {
                                        "label": "Best result",
                                        "value": "best:min",
                                    },
                                    {
                                        "label": "Mean RSS",
                                        "value": "mem_mean:min",
                                    },
                                    {
                                        "label": "Peak RSS",
                                        "value": "mem_peak:min",
                                    },
                                ],
                                value=["best:min"],
                                id="directions-checklist",
                                className="directions-checklist",
                            ),
                            html.P(
                                id="placeholder",
                                style={"display": "none"},
                            ),
                        ],
                        className="pb-20",
                    ),
                    html.Div(
                        [
                            html.P(
                                [
                                    "Feijoa code on ",
                                    html.A(
                                        children="GitHub.",
                                        target="_blank",
                                        href="https://github.com/qnbhd/feijoa",
                                        className="green-ish",
                                    ),
                                ]
                            ),
                        ]
                    ),
                ],
                className="one-third column app__right__section",
            ),
            dcc.Store(id="problem-name"),
            dcc.Store(id="selected-features"),
        ]
    )
    return layout

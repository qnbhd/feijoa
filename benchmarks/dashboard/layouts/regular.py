import dash_bootstrap_components as dbc
from dash import dcc, html

graphs_layout = html.Div(
    [
        html.Div(
            [
                dcc.Graph(
                    id="live-update-graph",
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
                dcc.Interval(
                    id="interval-component1",
                    interval=2 * 1000,  # in milliseconds
                    n_intervals=0,
                ),
            ],
            # style={'padding': 10, 'flex': 1}
        ),
        html.Br(),
        html.Div(
            [
                dcc.Graph(id="live-update-graph1", style={"width": "100%"}),
            ],
            # style={'padding': 10, 'flex': 1},
        ),
        html.Br(),
        html.Div(
            [
                dcc.Graph(
                    id="live-update-graph-polar",
                    style={"width": "100%"},
                ),
            ],
            # style={'padding': 10, 'flex': 1},
        ),
    ],
    style={"width": "75%", "padding": "2rem 2rem 2rem 2rem"},
)

# noinspection PyCallingNonCallable
sidebar = html.Div(
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
        dbc.Select(
            id="problems_dropdown",
            options=[
                {"label": "Rosenbrock", "value": "rosenbrock"},
            ],
            value="rosenbrock",
            style={"height": "3rem", "fontSize": "10pt"},
        ),
        dcc.Interval(
            id="interval-component-dropdown",
            interval=1 * 500,  # in milliseconds
            n_intervals=0,
        ),
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
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "Time",
                                                    "value": "time",
                                                },
                                                {
                                                    "label": "Best result",
                                                    "value": "best",
                                                },
                                                {
                                                    "label": "Mean RSS",
                                                    "value": "rss_mean",
                                                },
                                                {
                                                    "label": "Peak RSS",
                                                    "value": "rss_peak",
                                                },
                                            ],
                                            value=["best"],
                                            id="directions-checklist",
                                            # className="directions-checklist",
                                        ),
                                    ]
                                ),
                                dbc.Checklist(
                                    options=[
                                        {"label": "Max", "value": 1},
                                        {"label": "Max", "value": 2},
                                        {"label": "Max", "value": 3},
                                        {"label": "Max", "value": 4},
                                    ],
                                    value=[1],
                                    id="checklist-input",
                                    switch=True,
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                                "justify-content": "space-between",
                            },
                        )
                    ],
                    title="Metrics",
                ),
            ],
            start_collapsed=True,
        ),
        html.Div(
            [
                html.Span(
                    "Settings",
                    className="subheader",
                ),
                html.Span("  |  "),
                html.Span(
                    "Set plot settings.",
                    className="small-text",
                ),
            ],
            className="pb-20",
        ),
        html.Div(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Markdown(r"$$\alpha$$-coef", mathjax=True),
                            dcc.Slider(
                                0,
                                1,
                                0.1,
                                value=0.1,
                                id="slider-alpha",
                            ),
                            dcc.Markdown(r"$$\beta$$-coef", mathjax=True),
                            dcc.Slider(0, 1, 0.1, value=0.1, id="slider-beta"),
                            dcc.Markdown(r"$$\gamma$$-coef", mathjax=True),
                            dcc.Slider(
                                0,
                                1,
                                0.1,
                                value=0.1,
                                id="slider-gamma",
                            ),
                        ],
                        title="Ranking Coefficients",
                    ),
                ],
                start_collapsed=True,
            )
        ),
        html.Div(
            html.Div(
                id="placeholder",
                style={"display": "none"},
            )
        ),
        html.Br(),
        html.Div(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Markdown(r"$$y$$-axis scale", mathjax=True),
                            dbc.RadioItems(
                                options=[
                                    {
                                        "label": "Linear",
                                        "value": "linear",
                                    },
                                    {"label": "Log", "value": "log"},
                                ],
                                value="linear",
                                id="yaxis-radio",
                            ),
                            # html.Div(
                            #     [
                            #         html.P(
                            #             [
                            #                 "Feijoa code on ",
                            #                 html.A(
                            #                     children="GitHub.",
                            #                     target="_blank",
                            #                     href="https://github.com/qnbhd/feijoa",
                            #                     # className="green-ish",
                            #                 ),
                            #             ]
                            #         ),
                            #     ]
                            # ),
                        ],
                        title="Other",
                    )
                ],
                start_collapsed=True,
            )
        ),
    ],
    style={
        "position": "fixed",
        "background-color": "black",
        "width": "25%",
        "height": "90%",
        "right": 0,
        "top": "5rem",
        "padding": "2rem 2rem 2rem 2rem",
        "font-size": "14px",
        "overflow-y": "auto",
    },
    id="sidebar",
)


# noinspection PyCallingNonCallable


def make_oracles_ranking_page(style_adds=None):
    style_adds = style_adds or {}
    base = html.Div(
        [
            graphs_layout,
            sidebar,
        ],
        style={
            "display": "flex",
            "flex-direction": "row",
            "align-items": "center",
            **style_adds,
        },
    )
    return base
    # return make_preloader_outlined_tree(base)


def make_home_page():
    return html.Div(
        [
            html.Img(src="../assets/intro-pic.svg"),
        ],
    )

    # className="two-thirds column app__left__section"

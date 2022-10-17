import json

from dash import dcc
from dash import html
from dash import Input
from dash import Output
from dash import State
import dash_bootstrap_components as dbc


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "width": "100%",
    "height": "5rem",
    "zIndex": 2,
    "borderBottomStyle": "solid",
    "borderBottomColor": "#5F9D00",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-top": "5rem",
    "height": "100vh",
    "width": "100vw",
    "margin-left": 0,
    "margin-right": 0,
    "padding": "2rem 1rem",
    "zIndex": 1,
    "overflow-y": "scroll",
}

navbar_content = [
    html.Div(
        [
            html.Img(
                src="assets/feijoa-logo.svg",
                width="45%",
                height="100%",
            ),
            html.Div(
                [
                    dbc.NavLink("Home", href="/home", active="exact"),
                    dbc.NavLink("Oracles", href="/", active="exact"),
                ],
                style={
                    "display": "flex",
                    "flex-direction": "row",
                    "align-items": "center",
                    "justify-content": "space-between",
                    "margin-left": "1em",
                    "gap": "1rem",
                },
            ),
        ],
        style={"display": "flex", "flex-direction": "row"},
    ),
    html.Div(
        [
            dbc.Switch(id="theme-switch", value=False),
            html.Img(
                src="assets/light-toggle.svg",
                id="theme-toggle-pic",
                height="26px",
                width="26px",
            ),
        ],
        style={
            "display": "flex",
            "flex-direction": "row",
            "align-items": "center",
        },
        id="switch-bar",
    ),
]

sidebar = dbc.Nav(
    html.Div(
        [
            html.Div(
                navbar_content,
                style={
                    "display": "flex",
                    "flex-direction": "row",
                    "justify-content": "space-between",
                    "margin-left": "2rem",
                    "margin-right": "2rem",
                    "height": "5rem",
                },
                id="navbar-content",
            ),
            dcc.Store(id="dummy_theme"),
            html.Div(id="blank_output"),
            dcc.Store(id="theme"),
        ],
        style=SIDEBAR_STYLE,
        id="navbar",
    ),
    pills=True,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

outlined_content = html.Div(
    id="outlined-page-content",
    style={**CONTENT_STYLE, "position": "absolute", "zIndex": 0},
)

layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        outlined_content,
        content,
        html.Div(
            [
                html.Div(className="dark-mode"),
                dcc.Store(id="yaxis-scale"),
                dcc.Store(id="problem-name"),
                dcc.Store(id="selected-features"),
                dcc.Store(id="coefficients"),
                dcc.Store(id="n_changes_theme", data=json.dumps(0)),
                dcc.Store(id="directions"),
                dcc.Interval(
                    id="interval-outlining",
                    interval=1 * 5000,
                    n_intervals=0,
                    max_intervals=1,
                ),
            ],
            className="container-anim",
        ),
    ],
    style={"height": "100vh", "width": "100vw", "overflow": "hidden"},
)


def pickup_span_layout():
    return layout


def pickup_nav_content():
    return navbar_content

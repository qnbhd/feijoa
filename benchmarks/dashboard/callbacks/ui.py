import json
import time

from benchmarks.dashboard.dash_mixin import dashed
from benchmarks.dashboard.layouts.outlined import (
    make_oracles_ranking_page_outlined,
)
from benchmarks.dashboard.layouts.outlined import (
    make_outlined_navbar_content,
)
from benchmarks.dashboard.layouts.regular import (
    make_oracles_ranking_page,
)
from benchmarks.dashboard.layouts.regular import make_home_page
from benchmarks.dashboard.layouts.span import pickup_nav_content
from dash import html
from dash import Input
from dash import Output
from dash import State


DELAY = 1.0


@dashed(
    Output("problems_dropdown", "style"),
    Input("theme", "data"),
    State("problems_dropdown", "style"),
    State("n_changes_theme", "data"),
)
def update_problems_dropdown_theme(theme, style, n):
    time.sleep(DELAY)
    theme = json.loads(theme)
    style["background-color"] = (
        "black" if theme == "dark" else "white"
    )
    style["color"] = "#adafae" if theme == "dark" else "#343a40"
    style["border-color"] = "#adafae" if theme == "dark" else "black"
    style["border-width"] = "0.1rem"
    return style


@dashed(
    Output("sidebar", "style"),
    State("sidebar", "style"),
    Input("theme", "data"),
)
def update_side(side, value):
    time.sleep(DELAY)
    side["background-color"] = (
        "#111111" if json.loads(value) == "dark" else "#f4f4f4"
    )
    return side


@dashed(
    Output("page-content", "style"),
    State("page-content", "style"),
    Input("theme", "data"),
)
def update_pg(pg_content, value):
    time.sleep(DELAY)
    pg_content["background-color"] = (
        "black" if json.loads(value) == "dark" else "white"
    )
    return pg_content


@dashed(
    Output("navbar", "style"),
    State("navbar", "style"),
    Input("theme", "data"),
)
def update_nav(side, value):
    time.sleep(DELAY)
    # side["background-color"] = (
    #     "black" if json.loads(value) == "dark" else "white"
    # )
    return side


@dashed(
    Output("theme", "data"),
    Output("n_changes_theme", "data"),
    Input("theme-switch", "value"),
    State("n_changes_theme", "data"),
)
def update_theme(value, n):
    return json.dumps("white" if value else "dark"), json.dumps(
        json.loads(n) + 1
    )


@dashed(
    Output("theme-toggle-pic", "src"),
    Input("theme", "data"),
)
def update_toggle_pick(value):
    time.sleep(DELAY)
    return (
        "assets/light-toggle.svg"
        if json.loads(value) == "dark"
        else "assets/dark-toggle.svg"
    )


@dashed(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("interval-outlining", "n_intervals"),
)
def render_page_content(pathname, ticks):
    style = {"visibility": "visible" if ticks >= 1 else "hidden"}

    if pathname == "/":
        return [
            make_oracles_ranking_page(style),
        ]
    elif pathname == "/home":
        return [
            make_home_page(),
        ]

    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


@dashed(
    Output("outlined-page-content", "children"),
    Output("outlined-page-content", "style"),
    Input("url", "pathname"),
    Input("interval-outlining", "n_intervals"),
    State("outlined-page-content", "style"),
)
def render_page_content_outlined(pathname, ticks, opc_style):
    if ticks > 0:
        opc_style["visibility"] = "hidden"
        return [], opc_style

    if pathname == "/":
        return [
            make_oracles_ranking_page_outlined(),
        ], opc_style
    elif pathname == "/home":
        return [
            make_home_page(),
        ], opc_style

    return (
        html.Div(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(
                    f"The pathname {pathname} was not recognised..."
                ),
            ],
            className="p-3 bg-light rounded-3",
        ),
        opc_style,
    )


@dashed(
    Output("navbar-content", "children"),
    Input("interval-outlining", "n_intervals"),
    State("navbar-content", "children"),
)
def update_navbar_outlining(ticks, nav):

    if ticks == 0:
        nav_c = make_outlined_navbar_content()
        return nav_c

    return pickup_nav_content()

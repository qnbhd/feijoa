from benchmarks.dashboard.utils import mk_preloader_comp
from dash import html


graphs_layout = html.Div(
    [
        html.Div(
            [
                mk_preloader_comp(width="100rem", height="30rem"),
            ],
        ),
        html.Br(),
        html.Div(
            [
                mk_preloader_comp(
                    width="100rem", height="30rem", zIndex=10
                ),
            ],
        ),
        html.Br(),
        html.Div(
            [
                mk_preloader_comp(width="100rem", height="30rem"),
            ],
        ),
    ],
    style={"width": "75%", "padding": "2rem 2rem 2rem 2rem"},
)

# noinspection PyCallingNonCallable
sidebar = html.Div(
    [
        mk_preloader_comp(),
        mk_preloader_comp(),
        mk_preloader_comp(),
        mk_preloader_comp(),
        mk_preloader_comp(),
        mk_preloader_comp(),
        mk_preloader_comp(),
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

navbar_content = [
    html.Div(
        [
            html.Div(
                [
                    mk_preloader_comp(width="14.5rem"),
                    mk_preloader_comp(
                        width="5.5rem",
                        height="3rem",
                        borderRadius="10%",
                        card_settings=dict(padding="0 0"),
                    ),
                    mk_preloader_comp(
                        width="5.5rem",
                        height="3rem",
                        borderRadius="10%",
                        card_settings=dict(padding="0 0"),
                    ),
                ],
                style={
                    "display": "flex",
                    "flex-direction": "row",
                    "align-items": "center",
                    "justify-content": "space-between",
                    "margin-left": "0em",
                    "gap": "0.5rem",
                },
            )
        ],
        style={"display": "flex", "flex-direction": "row"},
    ),
    html.Div(
        [
            mk_preloader_comp(
                width="5rem",
                height="3rem",
                borderRadius="10%",
                card_settings=dict(padding="0 0"),
            ),
        ],
        style={
            "display": "flex",
            "flex-direction": "row",
            "align-items": "center",
        },
    ),
]


def make_outlined_navbar_content():
    return navbar_content


def make_oracles_ranking_page_outlined(adds=None):
    adds = adds or {}
    base = html.Div(
        [
            graphs_layout,
            sidebar,
        ],
        style={
            "display": "flex",
            "flex-direction": "row",
            "align-items": "center",
            **adds,
        },
    )
    return base


def make_home_page_outlined():
    return html.Div(
        [
            html.Img(src="assets/intro-pic.svg"),
        ],
    )

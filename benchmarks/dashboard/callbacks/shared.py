import json

from benchmarks.dashboard.dash_mixin import dashed
from dash import Input
from dash import Output
import ujson


@dashed(
    Output("problem-name", "data"),
    Input("problems_dropdown", "value"),
)
def set_display_children(selected_value):
    return ujson.dumps(selected_value)


@dashed(
    Output("selected-features", "data"),
    Input("directions-checklist", "value"),
)
def update_features(value):
    return ujson.dumps(value)


@dashed(
    Output("yaxis-scale", "data"),
    Input("yaxis-radio", "value"),
)
def update_yaxis_scale(value):
    return ujson.dumps(value)


@dashed(
    Output("directions", "data"), Input("checklist-input", "value")
)
def update_directions(checks):
    return json.dumps(
        {
            "time": "max" if 1 in checks else "min",
            "best": "max" if 2 in checks else "min",
            "rss_mean": "max" if 3 in checks else "min",
            "rss_peak": "max" if 4 in checks else "min",
        }
    )


@dashed(
    Output("coefficients", "data"),
    Input("slider-alpha", "value"),
    Input("slider-beta", "value"),
    Input("slider-gamma", "value"),
)
def update_sliders(alpha, beta, gamma):
    return ujson.dumps({"alpha": alpha, "beta": beta, "gamma": gamma})

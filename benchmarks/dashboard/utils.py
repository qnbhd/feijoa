from dash import html


def parse_metrics_and_directions(features, directions):
    """
    Parse metrics and directions
    from features list.

    Args:
        features (list):
            List of features to
            parse.
        directions:
            List of directions to
            parse.

    Returns:
        metrics (list):
            List of metrics.
        directions (list):
            List of directions.

    """
    metrics = []
    dirs_ = []

    for feature in features:
        metrics.append(feature)
        dirs_.append(directions[feature])

    return metrics, dirs_


def mk_preloader_comp(card_settings=None, **kwargs):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        className="preloader-outlined-image",
                        style=kwargs,
                    )
                ],
                className="d-flex",
            )
        ],
        className="card-body item",
        style=(card_settings or {}),
    )

from feijoa import create_job
from feijoa.search.algorithms.bayesian import BayesianAlgorithm
from feijoa.search.algorithms.genetic import CMAES
from feijoa.search.algorithms.genetic import PSO
from feijoa.search.algorithms.randomized import RandomSearch
from feijoa.search.algorithms.templatesearch import (
    TemplateSearchAlgorithm,
)
from feijoa.search.bandit import ThompsonSampler
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Real
from feijoa.search.space import SearchSpace
from feijoa.utils.logging import init
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def pad(string: str, width: int, filler=" ", fill_chars=3):
    if len(string) <= width:
        return string
    return f"{string[:width - 3]}{filler * fill_chars}"


def plot_evaluations(job, params=None):
    df = job.get_dataframe(brief=True, only_good=True)
    objectives = df["objective_result"]
    df.drop(columns=["id", "objective_result"], inplace=True)
    params = params or df.columns

    if any([param not in df.columns for param in params]):
        raise ValueError("Unknown columns in specified job.")

    params_length = len(params)

    fig = make_subplots(rows=params_length, cols=params_length)

    for i, col_x in enumerate(params):
        for j, col_y in enumerate(params):
            if i > j:
                continue

            if i == j:
                fig.add_histogram(
                    x=df[col_x],
                    nbinsx=30,
                    row=i + 1,
                    col=i + 1,
                    marker=dict(
                        color="#330C73",
                    ),
                    opacity=0.75,
                )
                continue

            x = df[col_x]
            y = df[col_y]

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    marker=dict(
                        color=objectives,
                        colorscale="TealRose_r",
                        symbol="circle",
                        colorbar=dict(title="Objective result"),
                        line=dict(width=1, color="black"),
                    ),
                ),
                col=i + 1,
                row=j + 1,
            )

    fig.update_layout(
        title="Evaluations plot",
        showlegend=False,
        bargap=0.2,
        bargroupgap=0.1,
    )

    def cut(base, num):
        if num == 1:
            return base
        return base if num == 1 else f"{base}{num}"

    positions = [
        (
            *fig["layout"][cut("xaxis", i)]["domain"],
            *fig["layout"][cut("yaxis", i)]["domain"],
        )
        for i in range(1, params_length**2 + 1)
    ]

    positions = [
        (x0, x1, y0, y1)
        for (x0, x1, y0, y1) in positions
        if x0 == 0.0 or y0 == 0.0
    ]

    names = list(params) * 2

    for i, (x0, x1, y0, y1) in enumerate(positions):
        x = x0
        y = y0
        angle = 0

        if x == 0.0:
            x -= 0.05
            y = (y0 + y1) / 2
            angle = 270
        else:
            x = (x0 + x1) / 2 + 0.02
            y -= 0.08

        fig.add_annotation(
            dict(
                x=x,
                y=y,
                xref="paper",
                yref="paper",
                text=pad(names.pop(0), 10, filler="."),
                showarrow=False,
            ),
            textangle=angle,
        )

        if x0 == 0 and y0 == 0:
            x_ = (x0 + x1) / 2
            y_ = -0.08
            angle = 0
            fig.add_annotation(
                dict(
                    x=x_,
                    y=y_,
                    xref="paper",
                    yref="paper",
                    text=pad(names.pop(0), 10, filler="."),
                    showarrow=False,
                ),
                textangle=angle,
            )

    return fig


def objective(experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    z = experiment.params.get("z")
    w = experiment.params.get("w")
    fast = experiment.params.get("fast")
    u = (
        (
            (1.5 - x + x * y) ** 2
            + (2.25 - x + x * y**2) ** 2
            + (2.625 - x + x * y**3) ** 2
        )
        - 0.1 * z
        - 0.5 * w
    )

    if fast == "foo":
        u -= 10
    elif fast == "bar":
        pass
    else:
        u -= 5

    return u


def main():
    space = SearchSpace()

    init(verbose=True)

    space.insert(Real("x", low=0.0, high=3.0))
    space.insert(Real("y", low=0.0, high=1.0))
    space.insert(Real("z", low=0.0, high=1.0))
    space.insert(Real("w", low=0.0, high=1.0))
    space.insert(Categorical("fast", choices=["foo", "bar", "zoo"]))

    bayesian = BayesianAlgorithm(search_space=space)
    template = TemplateSearchAlgorithm(search_space=space)
    cmaes = CMAES(search_space=space)
    pso_ = PSO(search_space=space)
    rnd = RandomSearch(search_space=space)

    thompson = ThompsonSampler(bayesian, template, rnd, cmaes, pso_)

    job = create_job(search_space=space)
    job.do(
        objective,
        n_proc=-1,
        n_trials=100,
        algo_list=[thompson],
        progress_bar=True,
        use_numba_jit=True,
    )

    fig = plot_evaluations(job)
    fig.show()


if __name__ == "__main__":
    main()

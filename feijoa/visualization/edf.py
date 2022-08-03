from feijoa import create_job
from feijoa import Real
from feijoa import SearchSpace
import numpy as np
import plotly.graph_objs as go


def plot_edf(
    job,
    fig=None,
    name=None,
):
    name = name or job.name
    fig = fig or go.Figure()
    df = job.get_dataframe(brief=True)
    objectives = df["objective_result"]
    min_value, max_value = objectives.min(), objectives.max()
    lspace = np.linspace(min_value, max_value, 100)

    dist = np.array([np.sum(objectives <= x) for x in lspace]) / len(
        objectives
    )

    fig.add_trace(
        go.Scatter(
            x=lspace,
            y=dist,
            mode="lines",
            name=f"{name}",
        )
    )

    fig.update_layout(
        title="Empirical distribution plot",
        xaxis_title="Objective value",
        yaxis_title="Cumulative probability",
    )

    return fig


def objective(experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    return (
        (1.5 - x + x * y) ** 2
        + (2.25 - x + x * y**2) ** 2
        + (2.625 - x + x * y**3) ** 2
    )


def main():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=3.0))
    space.insert(Real("y", low=0.0, high=1.0))

    job = create_job(search_space=space)
    job.do(
        objective,
        n_proc=-1,
        n_trials=2000,
        algo_list=["grid"],
        progress_bar=True,
        use_numba_jit=True,
    )

    fig = plot_edf(job)
    fig.show()


if __name__ == "__main__":
    main()

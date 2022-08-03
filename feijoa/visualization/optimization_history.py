from feijoa import Real
from feijoa import SearchSpace
from feijoa.jobs.job import create_job
import plotly.graph_objs as go


def plot_optimization_history(
    job,
    mode="lines+markers",
    name=None,
    fig=None,
    only_best=True,
):
    df = job.get_dataframe(desc=True)
    obj = df["objective_result"]
    iterations = df["id"]
    name = name or job.name

    fig = fig or go.Figure()

    fig.add_trace(
        go.Scatter(
            x=iterations,
            y=obj,
            mode=mode,
            name=f"{name} bests",
        )
    )

    if not only_best:
        full_df = job.get_dataframe()
        fig.add_trace(
            go.Scatter(
                x=full_df["id"],
                y=full_df["objective_result"],
                mode="markers",
                name=name,
            )
        )

    fig.update_layout(
        title="Optimization history plot",
        xaxis_title="Iteration",
        yaxis_title="Objective value",
    )

    return fig


def plot_compare_jobs(
    *jobs,
    mode="lines+markers",
    fig=None,
    names=None,
):
    if isinstance(names, list) and len(names) != len(jobs):
        raise ValueError(f"Names must contains {len(jobs)} values.")

    names = names or [job.name for job in jobs]

    fig = fig or go.Figure()

    for job, name in zip(jobs, names):
        plot_optimization_history(job, mode, name, fig)

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

    space.insert(Real("x", low=0.0, high=5.0))
    space.insert(Real("y", low=0.0, high=2.0))

    job = create_job(search_space=space)
    job.do(objective, n_trials=30)

    fig = plot_optimization_history(job, only_best=False)
    fig.show()


if __name__ == "__main__":
    main()

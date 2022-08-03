from feijoa import create_job
from feijoa import Real
from feijoa import SearchSpace
import plotly.graph_objs as go


def plot_objective_hist(
    job,
    fig=None,
):
    fig = fig or go.Figure()
    df = job.get_dataframe(brief=True)

    fig.add_histogram(x=df["objective_result"], nbinsx=100)

    fig.update_layout(
        title="Objective result histogram",
        xaxis_title="Objective value",
        yaxis_title="Count",
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

    fig = plot_objective_hist(job)
    fig.show()


if __name__ == "__main__":
    main()

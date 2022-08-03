from datetime import datetime
import json
import logging
import sys

import click
from feijoa.utils.logging import init
from utils.extractor import extract
from utils.run_tools import continue_job
from utils.run_tools import run_job


print(sys.path)

now = datetime.now().strftime("%H-%M-%S_%m_%d_%Y")

init(verbose=True)

log = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@click.command(name="run")
@click.option("--toolchain", type=str, required=True)
@click.option("--search-space", type=str, required=True)
@click.option("--source-file", type=str, required=True)
@click.option("--iterations", type=int, default=5)
@click.option("--n-trials", type=int, default=100)
@click.option("--storage", type=str, default=f"sqlite:///{now}.db")
@click.option("--job-name", type=str, default=now)
def run_cmd(
    toolchain,
    search_space,
    source_file,
    n_trials,
    iterations,
    storage,
    job_name,
):
    init(verbose=True)
    baselines, job = run_job(
        toolchain,
        search_space,
        source_file,
        n_trials,
        iterations,
        storage,
        job_name,
        "time",
    )
    log.info("Baselines:")
    log.info(json.dumps(baselines, indent=2))
    print(job.dataframe)


@click.command(name="continue")
@click.option("--toolchain", type=str, required=True)
@click.option("--search-space", type=str, required=True)
@click.option("--source-file", type=str, required=True)
@click.option("--iterations", type=int, default=5)
@click.option("--storage", type=str, required=True)
@click.option("--job-name", type=str, required=True)
def continue_cmd(
    toolchain,
    search_space,
    source_file,
    n_trials,
    iterations,
    storage,
    job_name,
):
    init(verbose=True)
    baselines, job = continue_job(
        toolchain,
        search_space,
        source_file,
        n_trials,
        iterations,
        storage,
        job_name,
        "time",
    )
    log.info("Baselines:")
    log.info(baselines)
    print(job.dataframe)


@click.command(name="extract")
@click.option("--toolchain", type=str, required=True)
@click.option("--captured-cache", type=str)
@click.option(
    "--out-file", type=str, default="extracted_search_space.yaml"
)
def extract_cmd(toolchain, captured_cache, out_file):
    extract(toolchain)


cli.add_command(run_cmd)
cli.add_command(continue_cmd)
cli.add_command(extract_cmd)

if __name__ == "__main__":
    cli()

# MIT License
#
# Copyright (c) 2021-2022 Templin Konstantin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from datetime import datetime
import json
import logging
import os
import subprocess

import click

from feijoa.utils.logging import init
from examples.gcc.utils.extractor import extract
from examples.gcc.utils.run_tools import continue_job
from examples.gcc.utils.run_tools import run_job


now = datetime.now().strftime("%H-%M-%S_%m_%d_%Y")

init(verbose=True)

log = logging.getLogger(__name__)


def command_exists(command):
    try:
        devnull = open(os.devnull, "w")
        subprocess.call(
            [command], stdout=devnull, stderr=subprocess.STDOUT
        )
        return True
    except OSError:
        return False


def validate_cli_command(ctx, param, value):
    if not command_exists(value):
        raise click.BadParameter(
            f"CLI command `{value}` not founded."
        )
    return value


@click.group()
def cli():
    pass


@click.command(name="run")
@click.option(
    "--toolchain",
    type=str,
    callback=validate_cli_command,
    required=True,
)
@click.option("--search-space", type=click.File("r"), required=True)
@click.option("--source-file", type=click.File("r"), required=True)
@click.option("--iterations", type=int, default=5)
@click.option("--n-trials", type=int, default=100)
@click.option("--storage", type=str, default=f"sqlite:///{now}.db")
@click.option("--job-name", type=str, default=now)
@click.option("--optimizer", type=str, default="ucb<bayesian>")
def run_cmd(
    toolchain,
    search_space,
    source_file,
    n_trials,
    iterations,
    storage,
    job_name,
    optimizer,
):
    init(verbose=True)
    baselines, job = run_job(
        toolchain,
        search_space.name,
        source_file.name,
        n_trials,
        iterations,
        storage,
        job_name,
        "time",
        optimizer=optimizer,
    )
    log.info("Baselines:")
    log.info(json.dumps(baselines, indent=2))
    print(job.dataframe)


@click.command(name="continue")
@click.option(
    "--toolchain",
    type=str,
    callback=validate_cli_command,
    required=True,
)
@click.option("--source-file", type=click.File("r"), required=True)
@click.option("--iterations", type=int, default=5)
@click.option("--storage", type=str, required=True)
@click.option("--job-name", type=str, required=True)
@click.option("--optimizer", type=str, default="ucb<bayesian>")
def continue_cmd(
    toolchain,
    source_file,
    n_trials,
    iterations,
    storage,
    job_name,
    optimizer,
):
    init(verbose=True)
    baselines, job = continue_job(
        toolchain,
        source_file.name,
        n_trials,
        iterations,
        storage,
        job_name,
        "time",
        optimizer=optimizer,
    )
    log.info("Baselines:")
    log.info(baselines)
    print(job.dataframe)


@click.command(name="extract")
@click.option("--toolchain", type=str, required=True)
def extract_cmd(toolchain):
    extract(toolchain)


cli.add_command(run_cmd)
cli.add_command(continue_cmd)
cli.add_command(extract_cmd)

if __name__ == "__main__":
    cli()

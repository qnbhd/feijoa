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
@click.option("--source-file", type=str, required=True)
@click.option("--iterations", type=int, default=5)
@click.option("--storage", type=str, required=True)
@click.option("--job-name", type=str, required=True)
def continue_cmd(
    toolchain,
    source_file,
    n_trials,
    iterations,
    storage,
    job_name,
):
    init(verbose=True)
    baselines, job = continue_job(
        toolchain,
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
def extract_cmd(toolchain):
    extract(toolchain)


cli.add_command(run_cmd)
cli.add_command(continue_cmd)
cli.add_command(extract_cmd)

if __name__ == "__main__":
    cli()

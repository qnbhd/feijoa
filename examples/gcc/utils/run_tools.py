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
from contextlib import suppress
from functools import partial
import hashlib
import logging
import os
from os.path import abspath
from os.path import dirname
import platform
import random
from typing import Optional
from typing import Tuple
from typing import Union

import numpy

from feijoa.utils.imports import ImportWrapper


with ImportWrapper():
    from executor import ExternalCommandFailed, execute

from feijoa import create_job
from feijoa import Experiment
from feijoa import load_job
from feijoa import SearchSpace
from feijoa.search import ParametersVisitor
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Parameter
from feijoa.search.parameters import Real


log = logging.getLogger(__name__)

ERROR_RESULT = float("+inf")


class GccRenderer(ParametersVisitor):
    """GCC renderer visitor.

    Args:
        experiment (Experiment):
            Specified experiment.

    Raises:
        AnyError: If anything bad happens.

    """

    def __init__(self, experiment):
        super().__init__()
        self.experiment = experiment

    def get_value(self, param: Parameter) -> Union[str, float]:
        value = self.experiment.params[param.name]
        return value

    def visit_common(self, p: Parameter) -> Optional[str]:
        value = self.get_value(p)
        return f"{p.name}={value}" if value else None

    def visit_integer(self, p: Integer) -> Optional[str]:
        return self.visit_common(p)

    def visit_real(self, p: Real) -> Optional[str]:
        return self.visit_common(p)

    def visit_categorical(
        self, p: Categorical, **kwargs
    ) -> Optional[str]:
        value = self.get_value(p)
        if value:
            return f"{value}"
        return None


def render(
    experiment: Experiment, space: SearchSpace, renderer_cls
) -> str:
    """Render an experiment to cli flags.

    Args:
        experiment (Experiment):
            Specified experiment.
        space (SearchSpace):
            Search space instance.
        renderer_cls (type):
            Renderer class.

    Raises:
        AnyError: If anything bad happens.

    """

    renderer = renderer_cls(experiment)

    rendered = list()

    for p in space:
        result_ = p.accept(renderer)
        if not result_:
            continue
        rendered.append(result_)

    return " ".join(rendered)


def run_command_and_capture_stdout(command: str) -> Optional[str]:
    """Run a command and capture stdout.

    Args:
        command (str):
            CLI command.

    Raises:
        AnyError: If anything bad happens.

    """

    log.debug(f"RUN COMMAND:\n{command}")

    try:
        output = execute(command, capture=True)

        decoded = output.strip()
        if decoded:
            log.info(f"OUT: {decoded}")

        return decoded
    except ExternalCommandFailed as e:
        log.error(e.error_message)
        return None


def compile_source(
    toolchain: str, source_file: str, rendered_opts, out_file: str
) -> Optional[float]:
    """Compile the source file.

    Args:
        toolchain (str):
            Toolchain path.
        source_file (str):
            Source file path.
        rendered_opts (str):
            Rendered opt (cli-format)
        out_file (str):
            Temporary out file.

    Raises:
        AnyError: If anything bad happens.

    """

    system_name = platform.system()

    if system_name == "Linux":
        compile_cmd = (
            f"/usr/bin/time -f '%e' {toolchain} -o"
            f" {out_file} {source_file} {rendered_opts} 2>&1"
        )

    elif system_name == "Darwin":
        # gnu-time is required
        compile_cmd = (
            f"/usr/local/bin/gtime -f '%e' {toolchain} -o"
            f" {out_file} {source_file} {rendered_opts} 2>&1"
        )

    else:
        raise RuntimeError()

    stdout = run_command_and_capture_stdout(compile_cmd)

    if (
        stdout is not None
        and stdout.lstrip("-").replace(".", "").isdigit()
    ):
        compile_time = float(stdout)
    else:
        return None

    return compile_time


def run_binary(
    binary_name, iterations
) -> Optional[Tuple[float, float, float, float, float]]:
    """Measure binary file.

    Args:
        binary_name (str):
            Path to binary file.
        iterations (int):
            Number of iterations to get specified
            accuracy.

    Raises:
        AnyError: If anything bad happens.

    """
    system_name = platform.system()

    if system_name == "Linux":
        run_cmd = f"/usr/bin/time -f '%e' {binary_name} 2>&1"
    elif system_name == "Darwin":
        # gnu-time is required
        run_cmd = f"/usr/local/bin/gtime -f '%e' {binary_name} 2>&1"
    else:
        raise RuntimeError()

    buff: numpy.ndarray = numpy.array([])
    for _ in range(iterations):
        stdout = run_command_and_capture_stdout(run_cmd)

        if stdout is None:
            return None

        try:
            run_time = float(stdout)
        except ValueError:
            return None

        buff = numpy.append(buff, run_time)

    run_time = buff.mean()
    std = buff.std()
    cv = std / buff.mean()
    low = min(buff)
    high = max(buff)

    return run_time, std, cv, low, high


def get_binary_size(binary_name) -> Optional[float]:
    """Get the size of a binary file"""

    size_cmd = "wc -c {} | awk {}".format(binary_name, "'{print $1}'")
    size_out = run_command_and_capture_stdout(size_cmd)
    if size_out is not None and size_out.isdigit():
        return int(size_out)
    return None


def objective(
    experiment: Experiment,
    toolchain: str,
    search_space: SearchSpace,
    source_file: str,
    objective_metric: str,
    iterations: int,
):
    """Objective function for GCC example.

    Args:
        experiment (Experiment):
            Specified experiment.
        toolchain (str):
            Toolchain path.
        search_space (SearchSpace):
            Search space instance.
        source_file (str):
            Source file path.
        objective_metric (str):
            Name of objective metric.
        iterations (int):
            Count of iteration to get
            specified accuracy.

    Raises:
        AnyError: If anything bad happens.

    """

    metrics = {
        "compile_time": ERROR_RESULT,
        "time": ERROR_RESULT,
        "size": ERROR_RESULT,
        "std": ERROR_RESULT,
        "cv": ERROR_RESULT,
        "low": ERROR_RESULT,
        "high": ERROR_RESULT,
    }

    experiment.metrics = metrics

    config_hash = hashlib.sha256(
        str(hash(experiment.json())).encode()
    ).hexdigest()

    # TODO: check if file is exists and remove random.randint
    binary_out = config_hash + str(random.randint(1, 99999)) + ".out"
    binary_out = os.path.join(dirname(abspath(__file__)), binary_out)

    rendered_opts = render(experiment, search_space, GccRenderer)

    compile_result = compile_source(
        toolchain, source_file, rendered_opts, binary_out
    )

    if not compile_result:
        with suppress(FileNotFoundError):
            os.remove(binary_out)
        return experiment.metrics[objective_metric]

    experiment.metrics["compile_time"] = compile_result

    run_result = run_binary(binary_out, iterations)

    if not run_result:
        os.remove(binary_out)
        return experiment.metrics[objective_metric]

    run_time, std, cv, low, high = run_result

    experiment.metrics["time"] = run_time
    experiment.metrics["std"] = std
    experiment.metrics["cv"] = cv
    experiment.metrics["low"] = low
    experiment.metrics["high"] = high

    size = get_binary_size(binary_out)

    if not size:
        os.remove(binary_out)
        return experiment.metrics[objective_metric]

    os.remove(binary_out)
    return experiment.metrics[objective_metric]


def run_baselines(toolchain, source_file, iterations):
    """Runs the baselines flags set.

    Args:
        toolchain (str):
            Toolchain path.
        source_file (str):
            Source file path.
        iterations (int):
            Count of iteration to get
            specified accuracy.

    Raises:
        AnyError: If anything bad happens.

    """

    compile_source(
        toolchain,
        source_file,
        "-O3",
        os.path.join(dirname(abspath(__file__)), "baselineO3.out"),
    )
    compile_source(
        toolchain,
        source_file,
        "-O2",
        os.path.join(dirname(abspath(__file__)), "baselineO2.out"),
    )
    compile_source(
        toolchain,
        source_file,
        "-O1",
        os.path.join(dirname(abspath(__file__)), "baselineO1.out"),
    )

    run_time_o3, std_o3, cv_o3, low_o3, high_o3 = run_binary(
        os.path.join(dirname(abspath(__file__)), "baselineO3.out"),
        iterations,
    )
    run_time_o2, std_o2, cv_o2, low_o2, high_o2 = run_binary(
        os.path.join(dirname(abspath(__file__)), "baselineO2.out"),
        iterations,
    )
    run_time_o1, std_o1, cv_o1, low_o1, high_o1 = run_binary(
        os.path.join(dirname(abspath(__file__)), "baselineO1.out"),
        iterations,
    )

    baselines = {
        "O3": {
            "time": run_time_o3,
            "std": std_o3,
            "cv": cv_o3,
            "low": low_o3,
            "high": high_o3,
        },
        "O2": {
            "time": run_time_o2,
            "std": std_o2,
            "cv": cv_o2,
            "low": low_o2,
            "high": high_o2,
        },
        "O1": {
            "time": run_time_o1,
            "std": std_o1,
            "cv": cv_o1,
            "low": low_o1,
            "high": high_o1,
        },
    }

    return baselines


def run_gcc(
    job,
    toolchain,
    iterations,
    n_trials,
    source_file,
    objective_metric,
    algorithms=None,
):
    """Runs the GCC example.

    Args:
        job (Job):
            Job instance.
        toolchain (str):
            Toolchain path.
        source_file (str):
            Source file path.
        objective_metric (str):
            Name of objective metric.
        iterations (int):
            Count of iteration to get
            specified accuracy.
        algorithms:
            List of names, classes or specified instances
            of algorithms.

    Raises:
        AnyError: If anything bad happens.

    """

    # noinspection PyProtectedMember
    job._load_algo(algo_list=algorithms)

    baselines = run_baselines(toolchain, source_file, iterations)

    obj = partial(
        objective,
        search_space=job.search_space,
        source_file=source_file,
        objective_metric=objective_metric,
        iterations=iterations,
        toolchain=toolchain,
    )

    job.do(
        obj,
        n_trials=n_trials,
        n_jobs=-1,
        algo_list=["bayesian", "template", "random"],
        use_numba_jit=False,
    )

    return baselines, job


def run_job(
    toolchain,
    search_space_file,
    source_file,
    n_trials,
    iterations,
    storage,
    job_name,
    objective_metric,
    *algorithms,
):
    """Only run wrapper for GCC example.

    Args:
        search_space_file (str):
            Path to search space file.
        n_trials (int):
            Count of total trials.
        storage (Storage):
            Specified storage instance.
        job_name (str):
            Job name.
        toolchain (str):
            Toolchain path.
        source_file (str):
            Source file path.
        objective_metric (str):
            Name of objective metric.
        iterations (int):
            Count of iteration to get
            specified accuracy.
        algorithms:
            List of names, classes or specified instances
            of algorithms.

    Raises:
        AnyError: If anything bad happens.

    """

    algorithms = algorithms or ["bayesian"]

    space = SearchSpace.from_yaml_file(search_space_file)
    job = create_job(
        search_space=space, storage=storage, name=job_name
    )
    baselines, job = run_gcc(
        job,
        toolchain,
        iterations,
        n_trials,
        source_file,
        objective_metric,
        algorithms=algorithms,
    )
    return baselines, job


def continue_job(
    toolchain,
    source_file,
    n_trials,
    iterations,
    storage,
    job_name,
    objective_metric,
):
    """Continue command for GCC example.

    Args:
        n_trials (int):
            Count of total trials.
        storage (Storage):
            Specified storage instance.
        job_name (str):
            Job name.
        toolchain (str):
            Toolchain path.
        source_file (str):
            Source file path.
        objective_metric (str):
            Name of objective metric.
        iterations (int):
            Count of iteration to get
            specified accuracy.

    Raises:
        AnyError: If anything bad happens.

    """

    job = load_job(storage=storage, name=job_name)
    baselines, job = run_gcc(
        job,
        toolchain,
        iterations,
        n_trials,
        source_file,
        objective_metric,
    )
    return baselines, job

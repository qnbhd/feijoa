import logging
import hashlib
import os
import platform
import random
from os.path import abspath, dirname

import numpy

from polytune.models.configuration import Configuration
from polytune.search.renderer import Renderer
from polytune.search.space import from_yaml
from executor import execute
from polytune.utils.os_dispatch import UnknownOsException


NAME = 'gcc'
METRICS = ('time', 'compile_time', 'size')
SOURCE_FILE = os.path.join(dirname(abspath(__file__)), 'raytracer', 'raytracer.cpp')
SPACE_FILE = os.path.join(dirname(abspath(__file__)), 'space_minimal.yaml')
SPACE = from_yaml(SPACE_FILE)

log = logging.getLogger(__name__)


class GccRenderer(Renderer):

    def visit_integer(self, p):
        value = self.get_value(p)
        return f"--param {p.name}={value}"


def run_command(command: str):
    log.debug(f'RUN COMMAND:\n[cyan][bold]{command}')

    output = execute(command, capture=True)

    decoded = output.strip()
    if decoded:
        log.info(f'[yellow][bold]OUT: {decoded}')

    return decoded


def metric_collector(configuration: Configuration):
    rendered = configuration.render(SPACE, GccRenderer)

    config_hash = hashlib.sha256(str(hash(configuration)).encode()).hexdigest()

    # TODO: check if file is exists and remove random.randint
    binary_out = config_hash + str(random.randint(1, 99999)) + '.out'
    binary_out = os.path.join(dirname(abspath(__file__)), binary_out)

    system_name = platform.system()

    if system_name == 'Linux':
        compile_cmd = f'time -f \'%e\' g++ -o' \
                      f' {binary_out} {SOURCE_FILE} {rendered} 2>&1'

        run_cmd = f'time -f \'%e\' ./{binary_out} 2>&1'

    elif system_name == 'Darwin':
        # gnu-time is required
        compile_cmd = f'gtime -f \'%e\' g++-11 -o' \
                      f' {binary_out} {SOURCE_FILE} {rendered} 2>&1'
        run_cmd = f'gtime -f \'%e\' ./{binary_out} 2>&1'

    else:
        raise UnknownOsException()

    size_cmd = "wc -c {} | awk {}".format(binary_out, "'{print $1}'")


    try:
        compile_time = float(run_command(compile_cmd))
    except:
        run_command(f'rm {binary_out}')
        return {
            'time': None,
            'compile_time': None,
            'size': None,
        }

    try:
        size = int(run_command(size_cmd))
    except:
        size = None

    try:
        run_time = numpy.array([
            float(run_command(run_cmd))
            for _ in range(5)
        ]).mean()
    except:
        run_time = None

    run_command(f'rm {binary_out}')

    return {
        'time': run_time,
        'compile_time': compile_time,
        'size': size,
    }



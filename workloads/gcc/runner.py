import hashlib
import os
import random
from os.path import abspath, dirname

from polytune.models.configuration import Configuration
from polytune.search.renderer import Renderer
from polytune.search.space import from_yaml
from executor import execute

from utils import logging
from utils.os_dispatch import os_dispatch, UnknownOsException


NAME = 'gcc'
METRICS = ('time', 'size')
SOURCE_FILE = os.path.join(dirname(abspath(__file__)), 'raytracer', 'raytracer.cpp')
SPACE_FILE = os.path.join(dirname(abspath(__file__)), 'space.yaml')
SPACE = from_yaml(SPACE_FILE)

log = logging.getLogger(__name__)


def run_command(command: str):
    log.debug(f'RUN COMMAND:\n[cyan][bold]{command}')

    output = execute(command, capture=True)

    decoded = output.strip()
    if decoded:
        log.info(f'[yellow][bold]OUT: {decoded}')

    return decoded


def metric_collector(configuration: Configuration):
    rendered = configuration.render(SPACE, Renderer)

    config_hash = hashlib.sha256(str(hash(configuration)).encode()).hexdigest()
    binary_out = config_hash + str(random.randint(1, 99999)) + '.out'
    binary_out = os.path.join(dirname(abspath(__file__)), binary_out)

    @os_dispatch
    def run_assembling():
        raise UnknownOsException()

    @run_assembling.register('linux')
    def linux_implementation():
        run_command(f'g++ -o {binary_out} {SOURCE_FILE} {rendered}')
        return run_command(f'time -f \'%e\' ./{binary_out}')

    @run_assembling.register('darwin')
    def darwin_implementation():
        run_command(f'g++-11 -o {binary_out} {SOURCE_FILE} {rendered}')
        return run_command(f'gtime -f \'%e\' ./{binary_out} 2>&1')

    run_time = run_assembling()
    log.info(f'RUN TIME: {run_time}')

    size_cmd = "wc -c {} | awk {}".format(binary_out, "'{print $1}'")
    size = run_command(size_cmd)

    run_command(f'rm {binary_out}')

    return {'time': float(run_time), 'size': int(size)}

import json
import logging
import os
from os.path import abspath
from os.path import dirname
import re

from feijoa.utils.imports import ImportWrapper


with ImportWrapper():
    import executor

log = logging.getLogger(__name__)

APPLICATION = os.path.join(
    dirname(dirname(abspath(__file__))), "raytracer", "raytracer.cpp"
)


def check_is_working_flag(gcc_toolchain_path, flag):
    cmd = f"{gcc_toolchain_path} {APPLICATION} {flag} 2>&1"
    try:
        result = executor.execute(cmd, capture=True)
    except executor.ExternalCommandFailed:
        return False
    return result == ""


def invert_gcc_flag(flag_):
    assert flag_[:2] == "-f"
    if flag_[2:5] != "no-":
        return "-fno-" + flag_[2:]
    return "-f" + flag_[5:]


def parse_optimizers(gcc_toolchain_path):
    try:
        result = executor.execute(
            f"{gcc_toolchain_path} --help=optimizers -Q", capture=True
        )
    except executor.ExternalCommandFailed:
        return {}

    out = result.split("\n")[1:]

    O_num_pat = re.compile("-O<number>")
    flag_align_eq_pat = re.compile("-f(align-[-a-z]+)=")
    flag_pat = re.compile("-f([-a-z0-9]+)")
    flag_enum_pat = re.compile(
        "-f([-a-z0-9]+)=\\[([-A-Za-z_\\|]+)\\]"
    )
    flag_interval_pat = re.compile(
        "-f([-a-z0-9]+)=<([0-9]+),([0-9]+)>"
    )
    flag_number_pat = re.compile("-f([-a-z0-9]+)=<number>")

    optimizers = {}

    def parse_line(line):
        bits = line.split()
        if not bits:
            return

        spec = bits[0]

        m = O_num_pat.fullmatch(spec)
        if m:
            choices = ["-O0", "-O1", "-O2", "-O3"]
            optimizers["-O"] = {
                "type": "categorical",
                "choices": choices,
            }
            return

        # -falign-str=
        m = flag_align_eq_pat.fullmatch(spec)
        if m:
            choices = []
            name = "-f" + m.group(1)

            if check_is_working_flag(gcc_toolchain_path, name):
                choices.append(name)

            inverted = invert_gcc_flag(name)

            if check_is_working_flag(gcc_toolchain_path, inverted):
                choices.append(inverted)

            choices.append(None)

            optimizers[name] = {
                "type": "categorical",
                "choices": choices,
            }
            return

        # -fflag
        m = flag_pat.fullmatch(spec)
        if m:
            choices = []
            name = "-f" + m.group(1)

            if check_is_working_flag(gcc_toolchain_path, name):
                choices.append(name)

            inverted = invert_gcc_flag(name)

            if check_is_working_flag(gcc_toolchain_path, inverted):
                choices.append(inverted)

            choices.append(None)

            optimizers[name] = {
                "type": "categorical",
                "choices": choices,
            }
            return

        # -fflag=[a|b]
        m = flag_enum_pat.fullmatch(spec)
        if m:
            name = "-f" + m.group(1)
            values = m.group(2).split("|")
            values = [f"{name}={v}" for v in values]
            optimizers[name] = {
                "type": "categorical",
                "choices": values,
            }
            return

        # -fflag=<min, max>
        m = flag_interval_pat.fullmatch(spec)
        if m:
            name = "-f" + m.group(1)
            minimum = int(m.group(2))
            maximum = int(m.group(3))
            if minimum < maximum:
                optimizers[name] = {
                    "type": "integer",
                    "range": [minimum, maximum],
                }
            return

        # -fflag=<number>
        m = flag_number_pat.fullmatch(spec)
        if m:
            name = "-f" + m.group(1)
            minimum = 0
            maximum = 2 << 31 - 1
            optimizers[name] = {
                "type": "integer",
                "range": [minimum, maximum],
            }
            return

        log.warning(f"Unknown optimizer {line}")

    for line_ in out:
        parse_line(line_)

    return optimizers


def parse_parameters(gcc_toolchain_path):
    try:
        result = executor.execute(
            f"{gcc_toolchain_path} --help=params -Q", capture=True
        )
    except executor.ExternalCommandFailed:
        return {}

    out = result.split("\n")[1:]

    param_enum_pat = re.compile(
        "--param=([-a-zA-Z0-9]+)=\\[([-A-Za-z_\\|]+)\\]"
    )
    param_interval_pat = re.compile(
        "--param=([-a-zA-Z0-9]+)=<(-?[0-9]+),([0-9]+)>"
    )
    param_number_pat = re.compile("--param=([-a-zA-Z0-9]+)=")
    param_old_interval_pat = re.compile(
        "\\s+([-a-zA-Z0-9]+)\\s+default\\s+(-?\\d+)\\s"
        "+minimum\\s+(-?\\d+)\\s+maximum\\s+(-?\\d+)"
    )

    params = {}

    def parse_line(line: str):
        bits = line.split()
        if not bits:
            return

        if len(bits) <= 1:
            return

        if len(bits) > 2:
            spec = line
        else:
            spec = bits[0]

        spec = spec.strip()

        # --param=name=[a|b]
        m = param_enum_pat.fullmatch(spec)
        if m:
            name = "--param=" + m.group(1)
            values = m.group(2).split("|")
            values = [f"{name}={v}" for v in values]

            params[name] = {"type": "categorical", "choices": values}
            log.info(f"Categorical: {name} {values}")
            return

        m = param_interval_pat.fullmatch(spec)
        if m:
            name = "--param=" + m.group(1)
            minimum = int(m.group(2))
            maximum = int(m.group(3))
            if minimum < maximum:
                params[name] = {
                    "type": "integer",
                    "range": [minimum, maximum],
                }
            log.info(f"Integer: {name} {minimum} {maximum}")
            return

        # --param=name=
        m = param_number_pat.fullmatch(spec)
        if m:
            name = "--param=" + m.group(1)
            minimum = 0
            maximum = 2 << 31 - 1

            params[name] = {
                "type": "integer",
                "range": [minimum, maximum],
            }
            log.info(f"Integer: {name} {minimum} {maximum}")
            return

        m = param_old_interval_pat.fullmatch(spec)
        if m:
            name = "--param=" + m.group(1)
            minimum = int(m.group(3))
            maximum = int(m.group(4))
            if minimum < maximum:
                params[name] = {
                    "type": "integer",
                    "range": [minimum, maximum],
                }
                log.info(f"Integer: {name} {minimum} {maximum}")
                return
            else:
                log.info(
                    f"Parameter {m.group(1)} has incorrect bounds."
                )

        log.warning(f"Unknown parameter {line}")

    for line_ in out:
        parse_line(line_)

    return params


cc_black_list_chunks = [
    "fipa",
    "live-patching",
    "logical-op-non-short-circuit",
    "prefetch-minimum-stride",
    "sched-autopref-queue-depth",
    "vect-max-peeling-for-alignment",
    "handle-exceptions",
    "fsave-optimization-record",
    "flive",
    "fassociative-math",
    "stack-protector",
    "threadsafe-statics",
    "pack-struct",
    "fstack-check",
    "clash_protection",
    "asan",
]


def fix_parameters(gcc_toolchain, all_params):
    def keep(param, value):
        for bcc in cc_black_list_chunks:
            if bcc in param:
                return False

        if value["type"] == "integer":
            if not check_is_working_flag(
                gcc_toolchain, f'{param}={value["range"][0]}'
            ):
                return False
        if value["type"] == "categorical":
            if not check_is_working_flag(
                gcc_toolchain, value["choices"][0]
            ):
                return False

        return True

    fixed = {p: v for p, v in all_params.items() if keep(p, v)}

    return fixed


def get_version(gcc_toolchain_path):
    try:
        result = executor.execute(
            f"{gcc_toolchain_path} --version", capture=True
        )
        spl = (
            result.split("\n")[0]
            .replace(" ", "_")
            .replace("(", "_")
            .replace(")", "_")
            .replace(".", "_")
        )
        spl = spl.replace("__", "_")
        return spl
    except executor.ExternalCommandFailed:
        return ""


def extract(gcc_toolchain_path):
    version = get_version(gcc_toolchain_path)
    if not version:
        raise RuntimeError("Toolchain isn't runnable")

    if not os.path.exists(f"{version}_params.json"):
        params = parse_parameters(gcc_toolchain_path)

        with open(f"{version}_params.json", "w") as f:
            f.write(json.dumps(params, indent=2))
    else:
        with open(f"{version}_params.json") as f:
            params = json.loads(f.read())

    if not os.path.exists(f"{version}_optimizers.json"):
        optimizers = parse_optimizers(gcc_toolchain_path)

        with open(f"{version}_optimizers.json", "w") as f:
            f.write(json.dumps(optimizers, indent=2))
    else:
        with open(f"{version}_optimizers.json") as f:
            optimizers = json.loads(f.read())

    all_optimizations = {**params, **optimizers}

    fixed = fix_parameters(gcc_toolchain_path, all_optimizations)

    print(fixed)

    template = """- signature: {}
  type: {}
  choices: {}\n\n"""

    integer_template = """- signature: {}
  type: {}
  range: {}\n\n"""

    out = open(f"{version}_search_space.yaml", "w")

    for k, v in fixed.items():
        flag_type = v["type"]
        if flag_type == "categorical":
            choices = (
                "["
                + ", ".join(
                    [u if u else "null" for u in v["choices"]]
                )
                + "]"
            )
            out.write(template.format(k, flag_type, choices))
        elif flag_type == "integer":
            out.write(
                integer_template.format(k, flag_type, v["range"])
            )

    out.close()

import logging
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from src.isanager.config import Config
from src.isanager.logs import get_logger
from src.isanager.helpers import replace_env_vars
import src.isanager.status as status_view

logger = get_logger(__name__)


def up(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tname = target.get("name")
        logger.debug(f"[{tname}] running command")
        success = execute(target.get("path"), ["docker", "compose", "up", "-d"])
        logger.debug(
            f"[{tname}] command run successfully"
            if success
            else f"[{tname}] command failed"
        )
    logger.info(f"{config.command} completed")


def down(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tname = target.get("name")
        logger.debug(f"[{tname}] running command")
        success = execute(target.get("path"), ["docker", "compose", "down"])
        logger.debug(
            f"[{tname}] command run successfully"
            if success
            else f"[{tname}] command failed"
        )
    logger.info(f"{config.command} completed")


def update(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tname = target.get("name")
        logger.debug(f"[{tname}] running command")
        success1 = execute(target.get("path"), ["docker", "compose", "pull"])
        success2 = execute(
            target.get("path"), ["docker", "compose", "up", "-d", "--force-recreate"]
        )
        success3 = execute(target.get("path"), ["docker", "image", "prune", "-f"])
        success = success1 and success2 and success3
        logger.debug(
            f"[{tname}] command run successfully"
            if success
            else f"[{tname}] command failed"
        )
    logger.info(f"{config.command} completed")


def recreate(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tname = target.get("name")
        logger.debug(f"[{tname}] running command")
        success = execute(
            target.get("path"), ["docker", "compose", "up", "-d", "--force-recreate"]
        )
        logger.debug(
            f"[{tname}] command run successfully"
            if success
            else f"[{tname}] command failed"
        )
    logger.info(f"{config.command} completed")


def logs(config: Config):
    logger.info(f"{config.command} started")
    target = config.get_targets()[0]
    tname = target.get("name")
    logger.debug(f"[{tname}] running command")
    cmd = ["docker", "compose", "logs"]
    if config.is_follow:
        cmd.append("-f")
    success = attach(target.get("path"), cmd)
    logger.debug(
        f"[{tname}] command run successfully"
        if success
        else f"[{tname}] command failed"
    )
    logger.info(f"{config.command} completed")


def status(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(service_status, targets))
    color = sys.stdout.isatty() and not os.getenv("NO_COLOR")
    try:
        print(status_view.render_table(rows, color))
        sys.stdout.flush()
    except BrokenPipeError:
        # reader went away (e.g. `| head`): point stdout at devnull so the
        # interpreter's final flush doesn't print a traceback
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    logger.info(f"{config.command} completed")


def service_status(target: dict) -> dict:
    row = {"name": target.get("name"), "group": target.get("group")}

    try:
        path = replace_env_vars(target.get("path"))
    except KeyError as e:
        return {**row, "state": status_view.ERROR, "error": e.args[0]}

    if not os.path.isdir(path):
        return {**row, "state": status_view.ERROR, "error": f"path not found: {path}"}

    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "-a", "--format", "json"],
            cwd=path,
            capture_output=True,
            text=True,
        )
    except OSError as e:
        # e.g. docker not on PATH, or no permission to enter the folder
        return {**row, "state": status_view.ERROR, "error": str(e)}
    if result.returncode != 0:
        stderr_lines = result.stderr.strip().splitlines()
        message = stderr_lines[0] if stderr_lines else "docker compose ps failed"
        logger.debug(f"[{row['name']}] {result.stderr.strip()}")
        return {**row, "state": status_view.ERROR, "error": message}

    try:
        containers = status_view.parse_ps_output(result.stdout)
    except ValueError:
        return {**row, "state": status_view.ERROR, "error": "unreadable docker output"}

    return {**row, **status_view.summarize(containers)}


def attach(path: str, cmd: list[str]) -> bool:
    path = replace_env_vars(path)
    try:
        return subprocess.run(cmd, cwd=path).returncode == 0
    except KeyboardInterrupt:
        return True


def execute(path: str, cmd: list[str]) -> bool:
    path = replace_env_vars(path)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=path,
        text=True,
        bufsize=1,
    )

    output_lines = []
    for line in process.stdout:
        line = line.rstrip()
        if line:
            output_lines.append(line)
            logger.debug(line)

    process.wait()
    success = process.returncode == 0

    if not success and output_lines and not logger.isEnabledFor(logging.DEBUG):
        logger.error("\n".join(output_lines))

    return success

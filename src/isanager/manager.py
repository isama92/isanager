import logging
import subprocess
from src.isanager.config import Config
from src.isanager.logs import get_logger
from src.isanager.helpers import replace_env_vars

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

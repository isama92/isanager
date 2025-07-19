import subprocess
from src.isanager.config import Config
from src.isanager.logs import get_logger

logger = get_logger(__name__)


def up(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tcode = target.get("code")
        logger.debug(f"[{tcode}] running command")
        success = execute(target.get("path"), ["docker", "compose", "up", "-d"])
        logger.debug(
            f"[{tcode}] command run successfully"
            if success
            else f"[{tcode}] command failed"
        )
    logger.info(f"{config.command} completed")


def down(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tcode = target.get("code")
        logger.debug(f"[{tcode}] running command")
        success = execute(target.get("path"), ["docker", "compose", "down"])
        logger.debug(
            f"[{tcode}] command run successfully"
            if success
            else f"[{tcode}] command failed"
        )
    logger.info(f"{config.command} completed")


def update(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tcode = target.get("code")
        logger.debug(f"[{tcode}] running command")
        success1 = execute(target.get("path")["docker", "compose", "pull"])
        success2 = execute(
            target.get("path"), ["docker", "compose", "up", "-d", "--force-recreate"]
        )
        success3 = execute(target.get("path"), ["docker", "image", "prune", "-f"])
        success = success1 and success2 and success3
        logger.debug(
            f"[{tcode}] command run successfully"
            if success
            else f"[{tcode}] command failed"
        )
    logger.info(f"{config.command} completed")


def recreate(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        tcode = target.get("code")
        logger.debug(f"[{tcode}] running command")
        success = execute(
            target.get("path"), ["docker", "compose", "up", "-d", "--force-recreate"]
        )
        logger.debug(
            f"[{tcode}] command run successfully"
            if success
            else f"[{tcode}] command failed"
        )
    logger.info(f"{config.command} completed")


def execute(path: str, cmd: list[str]) -> bool:
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path,
    )

    success = process.returncode == 0

    log = logger.debug if success else logger.error
    if process.stdout:
        log(process.stdout.decode().strip())
    if process.stderr:
        log(process.stderr.decode().strip())

    return success

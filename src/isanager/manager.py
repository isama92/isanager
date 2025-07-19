import subprocess
from src.isanager.config import Config
from src.isanager.logs import get_logger

logger = get_logger(__name__)


def up(config: Config):
    execute(config)


def down(config: Config):
    execute(config)


def update(config: Config):
    execute(config)


def execute(config: Config):
    logger.info(f"{config.command} started")
    targets = config.get_targets()
    for target in targets:
        path = target.get("path")
        logger.debug(f"setting working directory to '{path}'")
        # TODO: cd to path
        continue # TODO: remove me
        logger.debug(f"running command")
        success = run_command(["docker", "compose", config.command, "-d"])
        logger.error('command run successfully' if success else 'command failed')
    logger.info(f"{config.command} completed")


def run_command(command: list[str]) -> bool:
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    success = process.returncode == 0

    log = logger.debug if success else logger.error

    if process.stdout:
        log(process.stdout.decode().strip())
    if process.stderr:
        log(process.stderr.decode().strip())

    return success

from src.isanager.logs import get_logger
from yaml import safe_load as yaml_load
from os.path import exists as path_exists
from dotenv import load_dotenv
import argparse

logger = get_logger(__name__)

app_name = "isanager"
config_file_path = "config.yaml"
env_file_path = ".env"


def load_env() -> bool:
    if not path_exists(env_file_path):
        return False

    load_dotenv(env_file_path)

    return True


def load_config() -> dict | None:
    logger.debug(f"loading {config_file_path}")

    try:
        f = open(config_file_path, "r")
    except FileNotFoundError:
        logger.error(f"{config_file_path} not found")
        return None

    config = yaml_load(f)

    if not isinstance(config, dict):
        logger.error(f"{config_file_path} is empty or malformed")
        return None

    logger.debug(f"{config_file_path} loaded")

    return config


class Args:
    command: str | None
    target: str | None
    is_group: bool
    is_all: bool
    UP = "up"
    DOWN = "down"
    UPDATE = "update"

    def __init__(
        self,
        command: str | None = None,
        target: str | None = None,
        is_group: bool = False,
        is_all: bool = False,
    ):
        self.command = command
        self.target = target
        self.is_group = is_group
        self.is_all = is_all

    def to_dict(self):
        return {
            "command": self.command,
            "target": self.target,
            "is_group": self.is_group,
            "is_all": self.is_all,
        }

    def verify(self) -> bool:
        if self.command is None:
            logger.error("Command is required")
            return False

        if self.target is None and not self.is_all:
            logger.error("Target is required")
            return False

        if self.target is not None and self.is_all:
            logger.error("Is all cannot be used with target")
            return False

        if self.is_group and self.is_all:
            logger.error("Is group and is all together are not allowed")
            return False

        # TODO: check target exists in services/groups (if all is false)

        return True

    @staticmethod
    def load(arg_list: list[str] | None = None):
        parser = argparse.ArgumentParser(description="Manage your docker services")

        parser.add_argument(
            "command",
            type=str,
            choices=[Args.UP, Args.DOWN, Args.UPDATE],
            help="The command to run",
        )
        parser.add_argument(
            "target",
            type=str,
            nargs="?",
            help="The service or group the command will be executed on",
        )
        parser.add_argument(
            "-g",
            "--group",
            type=bool,
            action=argparse.BooleanOptionalAction,
            help="True if target is a group",
        )
        parser.add_argument(
            "-a",
            "--all",
            type=bool,
            action=argparse.BooleanOptionalAction,
            help="Target all services",
        )
        parser.set_defaults(
            all=False,
            group=False,
        )

        try:
            args = parser.parse_args(arg_list)
        except SystemExit:
            return Args()

        return Args(args.command, args.target, args.group, args.all)

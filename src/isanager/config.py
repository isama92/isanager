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


class Config:
    command: str | None
    target: str | None
    is_group: bool
    is_all: bool
    services: list
    UP = "up"
    DOWN = "down"
    UPDATE = "update"
    RECREATE = "recreate"

    def __init__(
        self,
        command: str | None = None,
        target: str | None = None,
        is_group: bool = False,
        is_all: bool = False,
        services: list | None = None,
    ):
        self.command = command.lower() if command is not None else None
        self.target = target.lower() if target is not None else None
        self.is_group = is_group
        self.is_all = is_all
        self.services = services if services is not None else []

    def to_dict(self):
        return {
            "command": self.command,
            "target": self.target,
            "is_group": self.is_group,
            "is_all": self.is_all,
            "services": self.services,
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

        if self.services is None or len(self.services) == 0:
            logger.error("Config `services` are required")
            return False

        # TODO: check all services have code and path
        # TODO: if service name is not set, set it equal to code

        if not self.is_all:
            check_key = "group" if self.is_group else "code"
            service_checks = [srv.get(check_key) for srv in self.services]
            if self.target not in service_checks:
                logger.error(f"Service {check_key} '{self.target}' does not exist")
                return False

        return True

    def get_targets(self) -> list:
        targets = []
        for srv in self.services:
            find_key = "group" if self.is_group else "code"
            if srv.get(find_key) == self.target:
                targets.append(srv)
        return targets

    @staticmethod
    def load_args(preset_args: list[str] | None = None) -> dict:
        logger.debug(f"loading args")
        parser = argparse.ArgumentParser(
            description="Manage your docker compose services"
        )

        parser.add_argument(
            "command",
            type=str,
            choices=[Config.UP, Config.DOWN, Config.UPDATE, Config.RECREATE],
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
            args = parser.parse_args(preset_args)
            logger.debug(f"args loaded")
            return vars(args)
        except SystemExit:
            logger.error(f"args load failed")
            return {}

    @staticmethod
    def load_configs(preset_config: dict | None = None) -> dict | None:
        logger.debug(f"loading {config_file_path}")

        if preset_config is not None:
            return preset_config

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

    @staticmethod
    def load(preset_args: list[str] | None = None, preset_configs: dict | None = None):
        args = Config.load_args(preset_args)
        configs = Config.load_configs(preset_configs)

        return Config(
            args.get("command"),
            args.get("target"),
            args.get("group", False),
            args.get("all", False),
            configs.get("services"),
        )

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
    targets: list[str]
    is_group: bool
    is_all: bool
    is_follow: bool
    services: list
    UP = "up"
    DOWN = "down"
    UPDATE = "update"
    RECREATE = "recreate"
    LOGS = "logs"

    def __init__(
        self,
        command: str | None = None,
        targets: list[str] | None = None,
        is_group: bool = False,
        is_all: bool = False,
        is_follow: bool = False,
        services: list | None = None,
    ):
        self.command = command.lower() if command is not None else None
        self.targets = [t.lower() for t in targets] if targets is not None else []
        self.is_group = is_group
        self.is_all = is_all
        self.is_follow = is_follow
        self.services = services if services is not None else []

    def to_dict(self):
        return {
            "command": self.command,
            "targets": self.targets,
            "is_group": self.is_group,
            "is_all": self.is_all,
            "is_follow": self.is_follow,
            "services": self.services,
        }

    def verify(self) -> bool:
        if self.command is None:
            logger.error("Command is required")
            return False

        if self.command == Config.LOGS and (
            self.is_group or self.is_all or len(self.targets) != 1
        ):
            logger.error("Logs only works with a single service")
            return False

        if self.is_follow and self.command != Config.LOGS:
            logger.error("Follow can only be used with logs")
            return False

        if len(self.targets) == 0 and not self.is_all:
            logger.error("Target is required")
            return False

        if len(self.targets) > 0 and self.is_all:
            logger.error("Is all cannot be used with target")
            return False

        if self.is_group and self.is_all:
            logger.error("Is group and is all together are not allowed")
            return False

        if self.services is None or len(self.services) == 0:
            logger.error("Config `services` are required")
            return False

        for srv in self.services:
            if srv.get("code") is None:
                logger.error("Service `code` is required")
                return False
            if srv.get("path") is None:
                logger.error("Service `path` is required")
                return False
            if srv.get("name") is None:
                srv["name"] = srv["code"]

        if not self.is_all:
            check_key = "group" if self.is_group else "code"
            service_checks = [srv.get(check_key) for srv in self.services]
            for target in self.targets:
                if target not in service_checks:
                    logger.error(f"Service {check_key} '{target}' does not exist")
                    return False

        return True

    def get_targets(self) -> list:
        if self.is_all:
            return self.services

        find_key = "group" if self.is_group else "code"
        targets = []
        for target in self.targets:
            for srv in self.services:
                if srv.get(find_key) == target and srv not in targets:
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
            choices=[Config.UP, Config.DOWN, Config.UPDATE, Config.RECREATE, Config.LOGS],
            help="The command to run",
        )
        parser.add_argument(
            "targets",
            type=str,
            nargs="*",
            help="The services or groups the command will be executed on",
        )
        parser.add_argument(
            "-g",
            "--group",
            action=argparse.BooleanOptionalAction,
            help="True if target is a group",
        )
        parser.add_argument(
            "-a",
            "--all",
            action=argparse.BooleanOptionalAction,
            help="Target all services",
        )
        parser.add_argument(
            "-f",
            "--follow",
            action=argparse.BooleanOptionalAction,
            help="Follow log output, only with logs",
        )
        parser.set_defaults(
            all=False,
            group=False,
            follow=False,
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
            args.get("targets"),
            args.get("group", False),
            args.get("all", False),
            args.get("follow", False),
            configs.get("services"),
        )

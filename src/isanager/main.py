import src.isanager.config as config
from src.isanager.logs import get_logger, set_basic_log_config
import src.isanager.manager as manager


def main():
    env_is_loaded = config.load_env()

    set_basic_log_config()
    logger = get_logger(__name__)

    logger.info(f"{config.app_name} started")

    logger.debug(
        "{} {}".format(config.env_file_path, "loaded" if env_is_loaded else "not found")
    )

    logger.debug("configuration loaded")

    configs = config.Config.load()

    if not configs.verify():
        return

    logger.debug("arguments loaded")

    if configs.command == configs.UP:
        manager.up(configs)
    elif configs.command == configs.DOWN:
        manager.down(configs)
    elif configs.command == configs.UPDATE:
        manager.update(configs)
    else:
        logger.error(f"unknown command '{configs.command}'")
        return

    logger.debug(f"{config.app_name} finished")


if __name__ == "__main__":
    main()

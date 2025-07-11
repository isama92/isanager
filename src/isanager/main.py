from src.isanager.config import (
    app_name,
    env_file_path,
    load_env,
    load_config,
    Args,
)
from src.isanager.logs import get_logger, set_basic_log_config


def main():
    env_loaded = load_env()

    set_basic_log_config()
    logger = get_logger(__name__)

    logger.info(f"{app_name} started")

    logger.debug("{} {}".format(env_file_path, "loaded" if env_loaded else "not found"))

    config = load_config()

    if config is None:
        return

    logger.debug("configuration loaded")

    args = Args.load()

    if not args.verify():
        return

    logger.debug("arguments loaded")


if __name__ == "__main__":
    main()

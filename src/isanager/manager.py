from src.isanager.config import Config


def up(config: Config):
    # TODO:
    # get service/s - list even f it's a single one so it can be looped regardless
    # loop services
    # get path of current service
    # go to path of current service
    # run cmd of current service
    print(config.command, config.target)


def down(config: Config):
    print(config.command, config.target)


def update(config: Config):
    print(config.command, config.target)

from os import getenv
from re import compile as re_compile


class MissingEnvVar(KeyError):
    """A `${VAR}` in a service path has no value. Still a KeyError, so
    existing callers are unaffected; `name` lets callers word their own
    message."""

    def __init__(self, name: str, folder: str):
        super().__init__(
            f"environment variable '{name}' is required, used in '{folder}'"
        )
        self.name = name


def replace_env_vars(folder: str) -> str:
    pattern = re_compile(r"\$\{([a-zA-Z0-9_]+)\}")

    def replacer(match):
        env_var_name = match.group(1)
        env_var = getenv(env_var_name)
        if env_var is None:
            raise MissingEnvVar(env_var_name, folder)
        return env_var

    folder = pattern.sub(replacer, folder)
    return folder

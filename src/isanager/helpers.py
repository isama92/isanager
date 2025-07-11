from os import getenv
from re import compile as re_compile


def replace_env_vars(folder: str) -> str:
    pattern = re_compile(r"\$\{([a-zA-Z0-9_]+)\}")

    def replacer(match):
        env_var_name = match.group(1)
        env_var = getenv(env_var_name)
        if env_var is None:
            raise KeyError(
                f"environment variable '{env_var_name}' is required, used in '{folder}'"
            )
        return env_var

    folder = pattern.sub(replacer, folder)
    return folder

# isanager

Manage your docker services.

Start, stop, and update your docker services. One by one, or all together.

## Compatibilities

Tested on:
- Ubuntu 24.04
- Debian 12

I don't think it works on Windows systems.

## Dependencies

Install all the dependencies by running `pip install -r requirements.txt`.

## Configuration

Run `cp .env.example .env` and `cp config.yaml.example config.yaml` to create the base config files and edit them as needed.

The `.env` variable will override the `config.yaml` variables.

`.env` supports environment variables, e.g. `VAR="${BACKUP_BASE_PATH}service_folder"`

All services paths can use ${} to add an environment variable in the path itself. e.g. `folder: "${YOUR_SERVICE_BASE_PATH}/your_service_files"` where the env variable `YOUR_SERVICE_BASE_PATH` is `/home/user/` will become `/home/user/your_service_files`. In this specific situations, env variables can only be named with letter numbers and underscores (`_`).

### Env List

- `LOG_LEVEL`: possible values are `error`, `warning`, `info`, `debug`, default is `error`

### TODOs
- add restart command

# isanager

Manage your docker compose services.

Start, stop, and update your docker compose services. One by one, by group, or all together.

## Compatibilities

Tested on:
- Ubuntu 24.04
- Debian 12

I don't think it works on Windows systems.

## Dependencies

Install all the dependencies by running `pip install -r requirements.txt`.

## Configuration

Run `cp .env.example .env` and `cp config.yaml.example config.yaml` to create the base config files and edit them as needed.

All services paths can use ${} to add an environment variable in the path itself. e.g. `path: "${YOUR_SERVICE_BASE_PATH}/your_service_folder"` where the env variable `YOUR_SERVICE_BASE_PATH` is `/home/user/` will become `/home/user/your_service_files`. In this specific situations, env variables can only be named with letter numbers and underscores (`_`).

### Env List

- `LOG_LEVEL`: possible values are `error`, `warning`, `info`, `debug`, default is `error`

## How to run
To run it I added the following function to my `.zshrc` (or `.bashrc`)
```bash
isanager() {
    pushd /path/to/isanager > /dev/null
    source venv/bin/activate
    python main.py "$@"
    deactivate
    popd > /dev/null
}
```
This way you can run it just by running `isanager`.
Eg.
- `isanager -h`
- `isanager up servicename`
- `isanager up`

## Available options

You have to specify at least one command between:
- up: will run `docker compose up -d`
- down: will run `docker compose down`
- update: will pull the images, recreate the container, and then prune the old images 
- recreate: will run `docker compose up -d --force-recreate`

The option `-a` will run the command for all the services.
Or you can specify a service/group between the ones declared in the config.yaml.
The option `-g` is used to specify the 2nd parameter is a group and not a service name.

Examples:
- `isanager up srvname`: will bring up the service called srvname
- `isanager up grpname -g`: will bring up all the services having the group grpname
- `isanager up -a`: will bring up all the services

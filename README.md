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
Or you can specify one or more services/groups between the ones declared in the config.yaml.
The option `-g` is used to specify the targets are groups and not service names.

Examples:
- `isanager up srvname`: will bring up the service called srvname
- `isanager update srv1 srv2`: will update the services called srv1 and srv2
- `isanager up grpname -g`: will bring up all the services having the group grpname
- `isanager up grp1 grp2 -g`: will bring up all the services having the group grp1 or grp2
- `isanager up -a`: will bring up all the services

## TODO

- [ ] Add a `pyproject.toml` with a `[project.scripts]` entry point so `pip install .` (or `pipx install .`) installs an `isanager` binary on PATH, replacing the `pushd`/`source venv`/`deactivate` shell-function in the README.
- [ ] Move imports from `src.isanager.X` to `isanager.X` so the CLI and `pytest` can be run from any directory, not just the repo root.
- [ ] Fix `Config.load()` crashing with `AttributeError` when `config.yaml` is missing or empty (`load_configs()` returns `None`, then `.get("services")` blows up).
- [ ] Make `manager.update()` short-circuit: if `docker compose pull` fails, skip `up --force-recreate` and `image prune` instead of recreating with the stale image.
- [ ] Make `main()` exit with a non-zero status code when any service command fails, instead of always returning 0.
- [ ] Catch `KeyError` from `replace_env_vars` inside `manager.execute` so a single bad path doesn't abort an `-a` batch.
- [ ] Print a one-line summary at the end of `-a` runs (e.g. `3 ok, 2 failed: foo, bar`) so failures aren't lost in the streamed output.
- [ ] Split `Config.verify()` so validation is pure: move the `srv["name"] = srv["code"]` defaulting into a separate normalization step at load time.
- [ ] Add tests for `manager.py` (mock `subprocess`) and for `helpers.replace_env_vars` (missing var, multiple vars, no match).

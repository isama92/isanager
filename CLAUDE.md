# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`isanager` is a small Python CLI that wraps `docker compose` to manage a fleet of services declared in `config.yaml`. It runs `up`, `down`, `update` (pull + force-recreate + image prune), or `recreate` against a single service, a named group of services, or all services.

Linux-only (tested on Ubuntu 24.04 and Debian 12). It shells out to the `docker` binary, so Docker must be installed and the user must have permission to run `docker compose`.

## Commands

All commands must be run from the repo root because imports are rooted at `src.isanager.*` (see "Import layout" below).

```bash
# Install deps (typically inside a venv)
pip install -r requirements.txt

# Run the CLI
python main.py <command> [target] [-g] [-a]

# Run tests
pytest                                          # all tests
pytest tests/test_config.py                     # one file
pytest tests/test_config.py::test_config_verify # one test
pytest -k "verify"                              # by keyword
```

There is no linter, formatter, or build step configured.

## Configuration

Two files at the repo root, both required at runtime:

- `.env` — currently only `LOG_LEVEL` (`error` | `warning` | `info` | `debug`, default `error`). Loaded via `python-dotenv`.
- `config.yaml` — defines `services:`. Each service entry has:
  - `code` (required) — the identifier passed as `target`
  - `path` (required) — working directory passed as `cwd` to `docker compose`. Supports `${VAR}` expansion (variable names limited to `[a-zA-Z0-9_]`); a missing env var raises `KeyError` and aborts that service.
  - `name` (optional) — display name in logs; defaults to `code` if omitted.
  - `group` (optional) — used with `-g` to target multiple services at once.

`Config.verify()` fails fast (returns `False`, `main()` exits) if `command` is missing, target/`-a` are inconsistent, `-g` and `-a` are combined, or `services` is empty/malformed.

## Architecture

Single-process CLI, no daemons, no state. Flow in `src/isanager/main.py:main`:

1. `config.load_env()` loads `.env` (best-effort; missing file is fine).
2. `logs.set_basic_log_config()` reads `LOG_LEVEL` and configures the root logger.
3. `Config.load()` parses argv via `argparse` **and** loads `config.yaml`, merging both into a single `Config` instance. `Config.load(preset_args, preset_configs)` accepts injected args/config — this is the seam the tests use to avoid touching the filesystem or argv.
4. `Config.verify()` validates the merged state and normalizes services (fills `name`).
5. Dispatch to `manager.up/down/update/recreate` based on `configs.command`.

`manager.py` is the only module that talks to Docker. Each command:
- calls `config.get_targets()` to resolve `target` + `is_group` + `is_all` → a list of service dicts,
- iterates and calls `execute(path, cmd)` per service,
- `execute()` runs `replace_env_vars(path)` on the cwd, then `subprocess.run` with captured stdout/stderr, logging at `debug` on success and `error` on failure. Failures are logged but the loop continues to the next service.

`update` is the only command that issues multiple docker invocations per service (`pull`, `up -d --force-recreate`, `image prune -f`); they run sequentially and `success` is the AND of all three.

### Import layout

Imports are written as `from src.isanager.X import ...` (absolute from repo root, with `src` in the path). This means **the CWD must be the repo root** when running `python main.py` or `pytest`. The `isanager()` shell function in the README handles this with `pushd`. If you add new modules, follow the same `src.isanager.*` convention rather than relative imports.

### Tests

`tests/test_config.py` is parametrized over (`argv`, `config_dict`, `expected`) tuples and exercises `Config.load(...).to_dict()` and `Config.verify()`. There are currently no tests for `manager.py` (it would require mocking `subprocess.run`); `pytest-mock` is listed but commented out in `requirements.txt`.

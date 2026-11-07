import json
import re

UP = "up"
DOWN = "down"
RESTARTING = "restarting"
ERROR = "error"

HEADERS = ["NAME", "GROUP", "STATUS", "HEALTH", "CONTAINERS", "UPTIME"]

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

_COLORS = {
    UP: _GREEN,
    DOWN: _RED,
    RESTARTING: _YELLOW,
    ERROR: _YELLOW,
    "healthy": _GREEN,
    "unhealthy": _RED,
    "starting": _YELLOW,
}

_COLUMN_GAP = "  "


def parse_ps_output(stdout: str) -> list[dict]:
    """Parse `docker compose ps --format json`.

    Compose >= 2.21 prints one JSON object per line, older versions print a
    single JSON array. Both are accepted.
    """
    stdout = stdout.strip()
    if not stdout:
        return []
    if stdout.startswith("["):
        return json.loads(stdout)
    return [json.loads(line) for line in stdout.splitlines() if line.strip()]


def _uptime(status: str) -> str:
    # "Up 3 days (healthy)" -> "3 days"
    status = re.sub(r"\s*\(.*\)\s*$", "", status or "")
    return re.sub(r"^Up\s+", "", status)


def summarize(containers: list[dict]) -> dict:
    running = [c for c in containers if c.get("State") == "running"]
    restarting = any(c.get("State") == "restarting" for c in containers)

    health_values = {c.get("Health") for c in running if c.get("Health")}
    if "unhealthy" in health_values:
        health = "unhealthy"
    elif "starting" in health_values:
        health = "starting"
    elif "healthy" in health_values:
        health = "healthy"
    else:
        health = ""

    return {
        # restarting only when nothing runs: a crash loop is neither up
        # nor a deliberate stop
        "state": UP if running else RESTARTING if restarting else DOWN,
        "health": health,
        "running": len(running),
        "total": len(containers),
        "uptime": _uptime(running[0].get("Status", "")) if running else "",
    }


def _paint(text: str, color: str | None, enabled: bool) -> str:
    if not enabled or not color:
        return text
    return f"{color}{text}{_RESET}"


def render_table(rows: list[dict], color: bool = False) -> str:
    """Render rows as an aligned table.

    Each row has `name`, `group` and `state`. Rows in the error state carry
    an `error` message, the others carry the keys returned by `summarize`.
    Widths are computed on plain text before colouring, because ANSI codes
    have no visible width but do count in `len()`.
    """
    cells = []
    for row in rows:
        # YAML may give ints (e.g. `code: 2024`), the table needs text
        name = str(row["name"])
        group = "-" if row.get("group") is None else str(row["group"])
        if row["state"] == ERROR:
            cells.append([name, group, ERROR, row.get("error", "")])
        else:
            cells.append(
                [
                    name,
                    group,
                    row["state"],
                    row.get("health", ""),
                    f"{row.get('running', 0)}/{row.get('total', 0)}",
                    row.get("uptime", ""),
                ]
            )

    # error messages are free text, so they don't widen the HEALTH column
    widths = [len(h) for h in HEADERS]
    for row_cells, row in zip(cells, rows):
        measured = row_cells[:3] if row["state"] == ERROR else row_cells
        for i, value in enumerate(measured):
            widths[i] = max(widths[i], len(value))

    def line(values: list[str], colorize: bool) -> str:
        parts = []
        last = len(values) - 1
        for i, value in enumerate(values):
            padded = value if i == last else value.ljust(widths[i])
            parts.append(_paint(padded, _COLORS.get(value) if i in (2, 3) else None, colorize))
        return _COLUMN_GAP.join(parts).rstrip()

    header = _paint(line(HEADERS, False), _BOLD, color)
    return "\n".join([header] + [line(c, color) for c in cells])

import pytest
from src.isanager.status import parse_ps_output, summarize, render_table


def _c(state="running", health="", status="Up 3 hours"):
    return {"State": state, "Health": health, "Status": status}


@pytest.mark.parametrize(
    "stdout,expected_len",
    [
        ("", 0),
        ("   \n", 0),
        ("[]", 0),
        ('[{"State": "running"}, {"State": "exited"}]', 2),
        ('{"State": "running"}\n{"State": "exited"}\n', 2),
        ('{"State": "running"}\n\n{"State": "exited"}', 2),
    ],
)
def test_parse_ps_output(stdout, expected_len):
    assert len(parse_ps_output(stdout)) == expected_len


def test_parse_ps_output_invalid():
    with pytest.raises(ValueError):
        parse_ps_output("not json")


@pytest.mark.parametrize(
    "containers,expected",
    [
        # fmt: off
        ([], {"state": "down", "health": "", "running": 0, "total": 0, "uptime": ""}),
        ([_c("exited", status="Exited (0) 2 days ago")], {"state": "down", "health": "", "running": 0, "total": 1, "uptime": ""}),
        ([_c("exited"), _c(), _c("exited")], {"state": "up", "health": "", "running": 1, "total": 3, "uptime": "3 hours"}),
        ([_c(health="healthy", status="Up 2 days (healthy)")], {"state": "up", "health": "healthy", "running": 1, "total": 1, "uptime": "2 days"}),
        ([_c(health="healthy"), _c(health="unhealthy")], {"state": "up", "health": "unhealthy", "running": 2, "total": 2, "uptime": "3 hours"}),
        ([_c(health="healthy"), _c(health="starting")], {"state": "up", "health": "starting", "running": 2, "total": 2, "uptime": "3 hours"}),
        ([_c(health="healthy"), _c()], {"state": "up", "health": "healthy", "running": 2, "total": 2, "uptime": "3 hours"}),
        # health of a stopped container is ignored
        ([_c(), _c("exited", health="unhealthy")], {"state": "up", "health": "", "running": 1, "total": 2, "uptime": "3 hours"}),
        # fmt: on
    ],
)
def test_summarize(containers, expected):
    assert summarize(containers) == expected


ROWS = [
    {"name": "Jellyfin", "group": "media", "state": "up", "health": "healthy", "running": 1, "total": 1, "uptime": "3 days"},
    {"name": "Gitea", "group": None, "state": "down", "health": "", "running": 0, "total": 1, "uptime": ""},
    {"name": "Broken", "group": "x", "state": "error", "error": "environment variable 'FOO' is required"},
]


def test_render_table_plain():
    lines = render_table(ROWS, color=False).splitlines()
    assert "\033" not in "\n".join(lines)
    assert lines[0].split() == ["NAME", "GROUP", "STATUS", "HEALTH", "CONTAINERS", "UPTIME"]
    status_col = lines[0].index("STATUS")
    assert lines[1][status_col:].startswith("up")
    assert lines[2][status_col:].startswith("down")
    assert lines[3][status_col:].startswith("error")
    assert "-" in lines[2].split()  # missing group placeholder
    assert lines[3].endswith("environment variable 'FOO' is required")
    assert all(line == line.rstrip() for line in lines)


def test_render_table_color():
    output = render_table(ROWS, color=True)
    assert "\033[32mup" in output
    assert "\033[32mhealthy" in output
    assert "\033[31mdown" in output
    assert "\033[33merror" in output
    assert "\033[32mJellyfin" not in output

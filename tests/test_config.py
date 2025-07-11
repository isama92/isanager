import pytest
from src.isanager.config import Args


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # fmt: off
        (["up", "abc"], {"command": "up", "target": "abc", "is_group": False, "is_all": False}),
        (["down", "abc", "-g"], {"command": "down", "target": "abc", "is_group": True, "is_all": False}),
        (["down", "abc", "--group"], {"command": "down", "target": "abc", "is_group": True, "is_all": False}),
        (["update"], {"command": "update", "target": None, "is_group": False, "is_all": False}),
        (["update", "-a"], {"command": "update", "target": None, "is_group": False, "is_all": True}),
        (["update", "--all"], {"command": "update", "target": None, "is_group": False, "is_all": True}),
        (["update", "-g", "-a"], {"command": "update", "target": None, "is_group": True, "is_all": True}),
        (["update", "abc", "-g", "-a"], {"command": "update", "target": "abc", "is_group": True, "is_all": True}),
        (["-g", "-a"], {"command": None, "target": None, "is_group": False, "is_all": False}),
        (["-g"], {"command": None, "target": None, "is_group": False, "is_all": False}),
        (["-a"], {"command": None, "target": None, "is_group": False, "is_all": False}),
        ([], {"command": None, "target": None, "is_group": False, "is_all": False}),
        # fmt: on
    ],
)
def test_args_to_dict(test_input, expected):
    assert Args.load(test_input).to_dict() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (["up", "abc"], True),
        (["down", "abc", "-g"], True),
        (["down", "abc", "--group"], True),
        (["update", "-a"], True),
        (["update", "--all"], True),
        (["update"], False),
        (["update", "-g", "-a"], False),
        (["update", "abc", "-g", "-a"], False),
        (["-g", "-a"], False),
        (["-g"], False),
        (["-a"], False),
        ([], False),
    ],
)
def test_args_verify(test_input, expected):
    assert Args.load(test_input).verify() == expected

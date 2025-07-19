import pytest
from src.isanager.config import Config


@pytest.mark.parametrize(
    "test_args,test_configs,expected",
    [
        # fmt: off
        (["up", "abc"], {'services': [{'code': 'abc'}]}, {"command": "up", "target": "abc", "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["down", "abc", "-g"], {'services': [{'code': 'abc', 'group': 'abc'}]}, {"command": "down", "target": "abc", "is_group": True, "is_all": False, 'services': [{'code': 'abc', 'group': 'abc'}]}),
        (["down", "abc", "--group"], {'services': [{'code': 'abc', 'group': 'abc'}]}, {"command": "down", "target": "abc", "is_group": True, "is_all": False, 'services': [{'code': 'abc', 'group': 'abc'}]}),
        (["update"], {'services': [{'code': 'abc'}]}, {"command": "update", "target": None, "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["update", "-a"], {'services': [{'code': 'abc'}]}, {"command": "update", "target": None, "is_group": False, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["update", "--all"], {'services': [{'code': 'abc'}]}, {"command": "update", "target": None, "is_group": False, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["update", "-g", "-a"], {'services': [{'code': 'abc'}]}, {"command": "update", "target": None, "is_group": True, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["update", "abc", "-g", "-a"], {'services': [{'code': 'abc'}]}, {"command": "update", "target": "abc", "is_group": True, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["recreate", "abc"], {'services': [{'code': 'abc'}]}, {"command": "recreate", "target": "abc", "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["-g", "-a"], {'services': [{'code': 'abc'}]}, {"command": None, "target": None, "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["-g"], {'services': [{'code': 'abc'}]}, {"command": None, "target": None, "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["-a"], {'services': [{'code': 'abc'}]}, {"command": None, "target": None, "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        ([], {'services': [{'code': 'abc'}]}, {"command": None, "target": None, "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["up", "abc"], {}, {"command": 'up', "target": 'abc', "is_group": False, "is_all": False, 'services': []}),
        (["up", "abc"], {'services': []}, {"command": 'up', "target": 'abc', "is_group": False, "is_all": False, 'services': []}),
        # fmt: on
    ],
)
def test_config_to_dict(test_args, test_configs, expected):
    assert Config.load(test_args, test_configs).to_dict() == expected


@pytest.mark.parametrize(
    "test_args,test_configs,expected",
    [
        # fmt: off
        (["up", "abc"], {'services': [{'code': 'abc'}]}, True),
        (["down", "abc", "-g"], {'services': [{'code': 'abc', 'group': 'abc'}]}, True),
        (["down", "abc", "--group"], {'services': [{'code': 'abc', 'group': 'abc'}]}, True),
        (["update", "-a"], {'services': [{'code': 'abc'}]}, True),
        (["update", "--all"], {'services': [{'code': 'abc'}]}, True),
        (["update"], {'services': [{'code': 'abc'}]}, False),
        (["update", "-g", "-a"], {'services': [{'code': 'abc'}]}, False),
        (["update", "abc", "-g", "-a"], {'services': [{'code': 'abc'}]}, False),
        (["recreate", "abc"], {'services': [{'code': 'abc'}]}, True),
        (["-g", "-a"], {'services': [{'code': 'abc'}]}, False),
        (["-g"], {'services': [{'code': 'abc'}]}, False),
        (["-a"], {'services': [{'code': 'abc'}]}, False),
        ([], {'services': [{'code': 'abc'}]}, False),
        (["up", "abc"], {}, False),
        (["up", "abc"], {'services': []}, False),
        # fmt: on
    ],
)
def test_config_verify(test_args, test_configs, expected):
    assert Config.load(test_args, test_configs).verify() == expected

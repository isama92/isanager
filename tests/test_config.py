import pytest
from src.isanager.config import Config


@pytest.mark.parametrize(
    "test_args,test_configs,expected",
    [
        # fmt: off
        (["up", "abc"], {'services': [{'code': 'abc'}]}, {"command": "up", "targets": ["abc"], "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["down", "abc", "-g"], {'services': [{'code': 'abc', 'group': 'abc'}]}, {"command": "down", "targets": ["abc"], "is_group": True, "is_all": False, 'services': [{'code': 'abc', 'group': 'abc'}]}),
        (["down", "abc", "--group"], {'services': [{'code': 'abc', 'group': 'abc'}]}, {"command": "down", "targets": ["abc"], "is_group": True, "is_all": False, 'services': [{'code': 'abc', 'group': 'abc'}]}),
        (["update"], {'services': [{'code': 'abc'}]}, {"command": "update", "targets": [], "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["update", "-a"], {'services': [{'code': 'abc'}]}, {"command": "update", "targets": [], "is_group": False, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["update", "--all"], {'services': [{'code': 'abc'}]}, {"command": "update", "targets": [], "is_group": False, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["update", "-g", "-a"], {'services': [{'code': 'abc'}]}, {"command": "update", "targets": [], "is_group": True, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["update", "abc", "-g", "-a"], {'services': [{'code': 'abc'}]}, {"command": "update", "targets": ["abc"], "is_group": True, "is_all": True, 'services': [{'code': 'abc'}]}),
        (["recreate", "abc"], {'services': [{'code': 'abc'}]}, {"command": "recreate", "targets": ["abc"], "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["-g", "-a"], {'services': [{'code': 'abc'}]}, {"command": None, "targets": [], "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["-g"], {'services': [{'code': 'abc'}]}, {"command": None, "targets": [], "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["-a"], {'services': [{'code': 'abc'}]}, {"command": None, "targets": [], "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        ([], {'services': [{'code': 'abc'}]}, {"command": None, "targets": [], "is_group": False, "is_all": False, 'services': [{'code': 'abc'}]}),
        (["up", "abc"], {}, {"command": 'up', "targets": ['abc'], "is_group": False, "is_all": False, 'services': []}),
        (["up", "abc"], {'services': []}, {"command": 'up', "targets": ['abc'], "is_group": False, "is_all": False, 'services': []}),
        (["update", "abc", "DEF"], {'services': [{'code': 'abc', 'group': 'g1'}, {'code': 'def', 'group': 'g1'}, {'code': 'ghi', 'group': 'g2'}]}, {"command": "update", "targets": ["abc", "def"], "is_group": False, "is_all": False, 'services': [{'code': 'abc', 'group': 'g1'}, {'code': 'def', 'group': 'g1'}, {'code': 'ghi', 'group': 'g2'}]}),
        (["up", "g1", "g2", "-g"], {'services': [{'code': 'abc', 'group': 'g1'}, {'code': 'def', 'group': 'g1'}, {'code': 'ghi', 'group': 'g2'}]}, {"command": "up", "targets": ["g1", "g2"], "is_group": True, "is_all": False, 'services': [{'code': 'abc', 'group': 'g1'}, {'code': 'def', 'group': 'g1'}, {'code': 'ghi', 'group': 'g2'}]}),
        # fmt: on
    ],
)
def test_config_to_dict(test_args, test_configs, expected):
    assert Config.load(test_args, test_configs).to_dict() == expected


@pytest.mark.parametrize(
    "test_args,test_configs,expected",
    [
        # fmt: off
        (["up", "abc"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, True),
        (["down", "abc", "-g"], {'services': [{'code': 'abc', 'path': '/srv/abc', 'group': 'abc'}]}, True),
        (["down", "abc", "--group"], {'services': [{'code': 'abc', 'path': '/srv/abc', 'group': 'abc'}]}, True),
        (["update", "-a"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, True),
        (["update", "--all"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, True),
        (["update"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, False),
        (["update", "-g", "-a"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, False),
        (["update", "abc", "-g", "-a"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, False),
        (["recreate", "abc"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, True),
        (["-g", "-a"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, False),
        (["-g"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, False),
        (["-a"], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, False),
        ([], {'services': [{'code': 'abc', 'path': '/srv/abc'}]}, False),
        (["up", "abc"], {}, False),
        (["up", "abc"], {'services': []}, False),
        (["update", "abc", "def"], {'services': [{'code': 'abc', 'path': '/srv/abc', 'group': 'g1'}, {'code': 'def', 'path': '/srv/def', 'group': 'g1'}, {'code': 'ghi', 'path': '/srv/ghi', 'group': 'g2'}]}, True),
        (["up", "g1", "g2", "-g"], {'services': [{'code': 'abc', 'path': '/srv/abc', 'group': 'g1'}, {'code': 'def', 'path': '/srv/def', 'group': 'g1'}, {'code': 'ghi', 'path': '/srv/ghi', 'group': 'g2'}]}, True),
        (["update", "abc", "xyz"], {'services': [{'code': 'abc', 'path': '/srv/abc', 'group': 'g1'}, {'code': 'def', 'path': '/srv/def', 'group': 'g1'}, {'code': 'ghi', 'path': '/srv/ghi', 'group': 'g2'}]}, False),
        (["update", "abc", "def", "-a"], {'services': [{'code': 'abc', 'path': '/srv/abc', 'group': 'g1'}, {'code': 'def', 'path': '/srv/def', 'group': 'g1'}, {'code': 'ghi', 'path': '/srv/ghi', 'group': 'g2'}]}, False),
        # fmt: on
    ],
)
def test_config_verify(test_args, test_configs, expected):
    assert Config.load(test_args, test_configs).verify() == expected


@pytest.mark.parametrize(
    "test_args,expected_codes",
    [
        # fmt: off
        (["update", "abc", "ghi"], ["abc", "ghi"]),
        (["update", "ghi", "abc"], ["ghi", "abc"]),
        (["update", "abc", "abc"], ["abc"]),
        (["up", "g1", "-g"], ["abc", "def"]),
        (["up", "g2", "g1", "-g"], ["ghi", "abc", "def"]),
        (["up", "g1", "g1", "-g"], ["abc", "def"]),
        (["up", "-a"], ["abc", "def", "ghi"]),
        # fmt: on
    ],
)
def test_config_get_targets(test_args, expected_codes):
    configs = {'services': [{'code': 'abc', 'group': 'g1'}, {'code': 'def', 'group': 'g1'}, {'code': 'ghi', 'group': 'g2'}]}
    targets = Config.load(test_args, configs).get_targets()
    assert [srv["code"] for srv in targets] == expected_codes

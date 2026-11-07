import pytest
from src.isanager.helpers import MissingEnvVar, replace_env_vars


def test_replace_env_vars(monkeypatch):
    monkeypatch.setenv("ISANAGER_TEST_BASE", "/srv")
    assert replace_env_vars("${ISANAGER_TEST_BASE}/app") == "/srv/app"


def test_replace_env_vars_missing(monkeypatch):
    monkeypatch.delenv("ISANAGER_TEST_MISSING", raising=False)
    with pytest.raises(MissingEnvVar) as exc:
        replace_env_vars("${ISANAGER_TEST_MISSING}/app")
    assert exc.value.name == "ISANAGER_TEST_MISSING"
    # still a KeyError with the original message for the other commands
    assert isinstance(exc.value, KeyError)
    assert exc.value.args[0] == "environment variable 'ISANAGER_TEST_MISSING' is required, used in '${ISANAGER_TEST_MISSING}/app'"

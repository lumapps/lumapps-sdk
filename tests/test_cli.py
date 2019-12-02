from lumapps.api.cli import load_config, parse_args, list_configs
from lumapps.api.utils import set_config, _conn

import pytest
from mock import patch, MagicMock


def test_load_config():
    with pytest.raises(SystemExit):
        api_info, auth_info, user = load_config(
            None, None, "ivo@managemybudget.net", "mmb"
        )


def test_arg_parser():
    with pytest.raises(SystemExit):
        arg_parser, args = parse_args()
    with pytest.raises(SystemExit):
        arg_parser, args = parse_args(["--user", "foo", "--email", "bar"])
    arg_parser, args = parse_args(["--user", "foo"])


@patch("lumapps.api.utils.get_conf_db_file", MagicMock(return_value=":memory:"))
def test_list_configs_1(capsys):
    global _conn
    _conn = None
    list_configs()
    assert capsys.readouterr().out.startswith("There are no saved configs")


@patch("lumapps.api.utils.get_conf_db_file", MagicMock(return_value=":memory:"))
def test_list_configs_2(capsys):
    global _conn
    _conn = None
    set_config("foo", "bar")
    list_configs()
    assert "foo" in capsys.readouterr().out

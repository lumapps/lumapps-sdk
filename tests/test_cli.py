import logging

from pytest import fixture, raises

from lumapps.api.cli import load_config, parse_args, list_configs, setup_logger
from lumapps.api.utils import ConfigStore, _get_conn, _set_sqlite_ok


@fixture(autouse=True)
def reset_env():
    _set_sqlite_ok(True)


def test_load_config():
    with raises(SystemExit):
        api_info, auth_info, user = load_config(
            None, None, "ivo@managemybudget.net", "mmb"
        )
    api_info, auth_info, user = load_config(None, None, "ivo@managemybudget.net", None)
    assert user == "ivo@managemybudget.net"
    assert api_info is None
    assert auth_info is None


def test_arg_parser():
    # with pytest.raises(SystemExit):
    #     arg_parser, args = parse_args()
    with raises(SystemExit):
        arg_parser, args = parse_args(["--user", "foo", "--email", "bar"])
    arg_parser, args = parse_args(["--user", "foo"])


def test_list_configs_1(capsys, mocker):
    mocker.patch("lumapps.api.utils.get_conf_db_file", return_value=":memory:")
    list_configs()
    assert capsys.readouterr().out.startswith("There are no saved configs")


def test_list_configs_2(capsys, mocker):
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn(":memory:"))
    ConfigStore.set("foo", "bar")
    list_configs()
    assert "foo" in capsys.readouterr().out


def test_list_configs_no_sqlite(capsys, mocker):
    mocker.patch("lumapps.api.utils._get_sqlite_ok", return_value=False)
    ConfigStore.set("foo", "bar")
    list_configs()
    err = capsys.readouterr().out
    assert "foo" not in err


def test_setup_logger():
    setup_logger()
    l2 = logging.getLogger()
    assert len(l2.handlers)

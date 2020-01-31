import logging
from json import load
from importlib import reload
from unittest.mock import PropertyMock

from pytest import fixture, raises
from requests.exceptions import HTTPError

import lumapps.api.utils
from lumapps.api.cli import load_config, parse_args, list_configs, setup_logger, main
from lumapps.api.utils import ConfigStore, _get_conn


@fixture(autouse=True)
def reset_env():
    reload(lumapps.api.utils)


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
    out = capsys.readouterr().out
    assert "foo" not in out


def test_setup_logger():
    setup_logger()
    l2 = logging.getLogger()
    assert len(l2.handlers)


def test_main_1(capsys, mocker):
    mocker.patch(
        "lumapps.api.cli.parse_args", return_value=parse_args(["--user", "foo"])
    )
    main()
    out = capsys.readouterr().out
    assert "usage" in out
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn(":memory:"))
    mocker.patch(
        "lumapps.api.cli.parse_args", return_value=parse_args(["-c"])
    )
    main()
    out = capsys.readouterr().out
    assert "no saved" in out
    mocker.patch(
        "lumapps.api.cli.parse_args", return_value=parse_args(["--token", "foo"])
    )
    with open("tests/test_data/lumapps_discovery.json") as fh:
        mocker.patch(
            "lumapps.api.client.ApiClient.discovery_doc",
            new_callable=PropertyMock,
            return_value=load(fh),
        )
    with raises(SystemExit):
        main()
    mocker.patch(
        "lumapps.api.cli.parse_args",
        return_value=parse_args(["--token", "foo", "user", "get"]),
    )
    with raises(HTTPError):
        main()

import logging
from json import load
from unittest.mock import PropertyMock

from pytest import fixture, raises

from lumapps.api.cli import (
    cast_params,
    list_configs,
    load_config,
    main,
    parse_args,
    setup_logger,
    store_config
)
from lumapps.api.utils import (
    ConfigStore,
    _DiscoveryCacheDict,
    _get_conn,
    _set_sqlite_ok,
    get_endpoints,
)


@fixture(autouse=True)
def reset_env():
    _DiscoveryCacheDict._cache.clear()
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
    auth_file = "tests/legacy/test_data/dummy_auth.json"
    api_info, auth_info, user = load_config(
        None, auth_file, "foo@managemybudget.net", None
    )
    assert auth_info["project_id"] == "foo"
    api_file = "tests/legacy/test_data/dummy_api.json"
    api_info, auth_info, user = load_config(
        api_file, auth_file, "foo@managemybudget.net", None
    )
    assert auth_info["project_id"] == "foo"
    assert api_info["name"] == "lumsites"


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
    mocker.patch("lumapps.api.cli.parse_args", return_value=parse_args(["-c"]))
    main()
    out = capsys.readouterr().out
    assert "no saved" in out
    mocker.patch(
        "lumapps.api.cli.parse_args", return_value=parse_args(["--token", "foo"])
    )
    with open("tests/legacy/test_data/lumapps_discovery.json") as fh:
        mocker.patch(
            "lumapps.api.client.BaseClient.discovery_doc",
            new_callable=PropertyMock,
            return_value=load(fh),
        )
    with raises(SystemExit):
        main()
    mocker.patch(
        "lumapps.api.cli.parse_args",
        return_value=parse_args(["--token", "foo", "user", "get"]),
    )
    with raises(SystemExit):
        main()


def test_cast_params():
    with open("tests/legacy/test_data/lumapps_discovery.json") as fh:
        discovery_doc = load(fh)
    endpoints = get_endpoints(discovery_doc)
    name_parts = ("customcontenttype", "list")
    params = {"includeInstanceSiblings": "yes"}
    cast_params(name_parts, params, endpoints)
    assert params["includeInstanceSiblings"] is True
    params = {"includeInstanceSiblings": "no"}
    cast_params(name_parts, params, endpoints)
    assert params["includeInstanceSiblings"] is False


def test_store_config():
    api_file = {}
    auth_file = {}
    user = "test"
    conf_name = "conf_test"

    store_config(api_file, auth_file, conf_name, user=user)
    c = load_config(None, None, None, conf_name=conf_name)
    assert c[2] == user
    assert c == (api_file, auth_file, user)

    c = load_config(api_file, auth_file, user, conf_name=conf_name)
    assert c[2] == user
    assert c == (api_file, auth_file, user)
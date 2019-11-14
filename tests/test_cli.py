from lumapps.api.cli import load_config, parse_args

import pytest


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

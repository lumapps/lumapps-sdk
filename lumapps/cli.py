#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import sys
import argparse
import json

from lumapps.utils import (
    ApiCallError,
    FILTERS,
    get_config_names,
    get_config,
    set_config,
)
from lumapps.client import ApiClient
import logging

LIST_CONFIGS = "***LIST_CONFIGS***"


def parse_args():
    s = ""
    for f in FILTERS:
        s += "\nMethods " + f + "\n"
        for pth in sorted(FILTERS[f]):
            s += "    " + pth + "\n"

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog="FILTERS:\n" + s,
    )
    add_arg = parser.add_argument
    add_arg(
        "api_method",
        nargs="*",
        metavar="METHOD_PART",
        help="API method with parameters in the form arg_name=value",
    )
    add_arg("--help", "-h", action="store_true")
    add_arg("--debug", "-d", action="store_true")
    add_arg("--api", help="JSON file", metavar="FILE")
    add_arg("--user", help="user to act on behalf")
    add_arg("--auth", help="JSON auth file", metavar="FILE")
    add_arg(
        "--token",
        help="a token can be gotten with " '"getToken customerId=... email=..."',
    )
    add_arg("--body-file", help="JSON POST data body file", metavar="FILE")
    add_arg(
        "-p",
        "--prune",
        action="store_true",
        help="Prune extraneous content based on methods being invoked. "
        "See below for filters used.",
    )
    add_arg(
        "--config",
        "-c",
        nargs="?",
        default=None,
        const=LIST_CONFIGS,
        help="SAVE/READ/LIST configuration(s): if a value is provided: "
        "SAVE when --auth or --api is specified, READ otherwise; if "
        "no value is provided: list saved configs",
        metavar="CONF_NAME",
    )
    add_arg(
        "body",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help=argparse.SUPPRESS,
    )
    return parser, parser.parse_args()


def list_configs():
    conf_names = get_config_names()
    if not conf_names:
        print("There are no saved configs")
        return
    print("Saved configs:")
    for conf_name in conf_names:
        print("  " + conf_name)


def load_config(api_file, auth_file, user, conf_name):
    if conf_name:
        conf = get_config(conf_name) or {}
        if not conf and not auth_file:
            sys.exit('config "{}" not found'.format(conf_name))
    else:
        conf = {}
    if auth_file:
        with open(auth_file) as fh:
            auth_info = json.load(fh)
    else:
        auth_info = conf.get("auth", None)
    if api_file:
        with open(api_file) as fh:
            api_info = json.load(fh)
    else:
        api_info = conf.get("api", None)
    if not user:
        user = conf.get("user", None)
    return api_info, auth_info, user


def store_config(api_info, auth_info, conf_name, user=None):
    set_config(conf_name, {"api": api_info, "auth": auth_info, "user": user})


def cast_params(method_parts, params, api):
    truths = ("True", "true", "1", "Yes", "yes", "sure", "yeah")
    method = api.methods[method_parts]
    method_params = method.get("parameters", {})
    for param in params:
        if method_params.get(param, {}).get("type", "") == "boolean":
            params[param] = params[param] in truths


def setup_logger():
    level = logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def main():
    arg_parser, args = parse_args()
    if args.debug:
        setup_logger()
    if not (args.auth or args.api or args.config or args.token):
        arg_parser.print_help()
        return
    if args.config == LIST_CONFIGS:
        list_configs()
        return
    api_info, auth_info, user = load_config(args.api, args.auth, args.user, args.config)
    api = ApiClient(auth_info, api_info, user=user, token=args.token, prune=args.prune)
    if args.config and (args.auth or args.api):
        store_config(api_info, auth_info, args.config, args.user)
    if not args.api_method:
        arg_parser.print_help()
        sys.exit(
            "\nNo API method specified. Found these:\n"
            + api.get_method_descriptions(sorted(api.methods))
        )
    method_parts = tuple(p for p in args.api_method if "=" not in p)
    if method_parts not in api.methods:
        sys.exit(api.get_matching_methods(method_parts))
    if args.help:
        print(api.get_help(method_parts, args.debug))
        return
    params = {
        p[0]: p[2] for p in (a.partition("=") for a in args.api_method if "=" in a)
    }
    if args.body_file:
        with open(args.body_file) as fh:
            params["body"] = json.load(fh)
    elif "body" in params:
        params["body"] = json.loads(params["body"])
    # elif not sys.stdin.isatty() and args.body:
    #     s = args.body.read()
    #     print('will loads this: {}'.format(s))
    #     params['body'] = json.loads(s)
    cast_params(method_parts, params, api)
    try:
        response = api.get_call(*method_parts, **params)
    except ApiCallError as err:
        sys.exit(err)
    print(json.dumps(response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()

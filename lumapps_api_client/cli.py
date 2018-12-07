#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import sys
import argparse
import json

from lumapps_api_client.lib import ApiClient, ApiCallError, get_conf, set_conf
import logging

LIST_CONFIGS = "***LIST_CONFIGS***"
FILTERS = {
    # content/get, content/list, ...
    "content/*": [
        "lastRevision",
        "authorDetails",
        "updatedByDetails",
        "writerDetails",
        "headerDetails",
        "customContentTypeDetails",
    ],
    # community/get, community/list, ...
    "community/*": [
        "lastRevision",
        "authorDetails",
        "updatedByDetails",
        "writerDetails",
        "headerDetails",
        "customContentTypeDetails",
        "adminsDetails",
        "usersDetails",
    ],
    # template/get, template/list, ...
    "template/*": ["properties/duplicateContent"],
    "community/post/*": [
        "authorDetails",
        "updatedByDetails",
        "mentionsDetails",
        "parentContentDetails",
    ],
    "comment/get": ["authorProperties", "mentionsDetails"],
    "comment/list": ["authorProperties", "mentionsDetails"],
}


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
        "-f",
        "--filter",
        action="store_true",
        help="Filter out content based on methods being invoked. "
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
    conf = get_conf()["configs"]
    if not conf:
        print("There are no saved configs")
        return
    print("Saved configs:")
    for conf_name in conf:
        print("  " + conf_name)


def load_config(api_file, auth_file, user, conf_name):
    if conf_name:
        configs = get_conf()["configs"]
        conf = configs.get(conf_name, {})
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
    conf = get_conf()
    conf["configs"][conf_name] = {"api": api_info, "auth": auth_info, "user": user}
    set_conf(conf)


def filter_results(method_parts, results):
    for filter_method in FILTERS:
        filter_method_parts = filter_method.split("/")
        if len(method_parts) != len(filter_method_parts):
            continue
        for filter_part, part in zip(filter_method_parts, method_parts):
            if filter_part not in ("*", part):
                break
        else:
            for pth in FILTERS[filter_method]:
                if isinstance(results, list):
                    for o in results:
                        pop_matches(pth, o)
                else:
                    pop_matches(pth, results)


def pop_matches(dpath, d):
    if not dpath:
        return
    for pth_part in dpath.split("/")[:-1]:
        if not isinstance(d, dict):
            return
        d = d.get(pth_part)
    if not isinstance(d, dict):
        return
    d.pop(dpath.rpartition("/")[2], None)


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
    api = ApiClient(auth_info, api_info, user=user, token=args.token)
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
    if args.filter:
        filter_results(method_parts, response)
    print(json.dumps(response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()

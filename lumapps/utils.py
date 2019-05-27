import os
import json
from datetime import datetime, timedelta

from lumapps.config import __pypi_packagename__

GOOGLE_APIS = ("drive", "admin", "groupssettings")
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
    "communitytemplate/*": [
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


def get_conf_file():
    if "APPDATA" in os.environ:
        d = os.environ["APPDATA"]
    elif "XDG_CONFIG_HOME" in os.environ:
        d = os.environ["XDG_CONFIG_HOME"]
    else:
        d = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(d, "{}.conf".format(__pypi_packagename__))


def get_conf():
    try:
        with open(get_conf_file()) as fh:
            conf = json.load(fh)
    except IOError:
        return {"configs": {}, "cache": {}}
    if not conf:
        conf = {"configs": {}, "cache": {}}
    return conf


def set_conf(conf):
    try:
        with open(get_conf_file(), "wt") as fh:
            return json.dump(conf, fh, indent=4)
    except IOError:
        pass


class ApiCallError(Exception):
    pass


class DiscoveryCache(object):
    _max_age = 60 * 60 * 24  # 1 day

    @staticmethod
    def get(url):
        cached = get_conf()["cache"].get(url)
        if not cached:
            return None
        expiry_dt = datetime.strptime(cached["expiry"][:19], "%Y-%m-%dT%H:%M:%S")
        if expiry_dt < datetime.now():
            return None
        return cached["content"]

    @staticmethod
    def set(url, content):
        conf = get_conf()
        conf["cache"][url] = {
            "expiry": (
                datetime.now() + timedelta(seconds=DiscoveryCache._max_age)
            ).isoformat()[:19],
            "content": content,
        }
        set_conf(conf)

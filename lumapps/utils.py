import os
import sqlite3
from json import loads, dumps
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


def get_conf_db_file():
    if "APPDATA" in os.environ:
        d = os.environ["APPDATA"]
    elif "XDG_CONFIG_HOME" in os.environ:
        d = os.environ["XDG_CONFIG_HOME"]
    else:
        d = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(d, "{}.db".format(__pypi_packagename__))


def _get_conn():
    conn = sqlite3.connect(get_conf_db_file())
    conn.isolation_level = None
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute(
        """CREATE TABLE IF NOT EXISTS discovery_cache (
            url TEXT NOT NULL,
            expiry TEXT NOT NULL,
            content TEXT NOT NULL,
            PRIMARY KEY (url)
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS config (
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            PRIMARY KEY (name)
        )"""
    )
    return conn


def get_discovery_cache(url):
    try:
        return _get_conn().execute(
            "SELECT * FROM discovery_cache WHERE url=?", (url,)
        ).fetchone()
    except sqlite3.OperationalError:
        return None


def set_discovery_cache(url, expiry, content):
    try:
        _get_conn().execute(
            "INSERT OR REPLACE INTO discovery_cache VALUES (?, ?, ?)",
            (url, expiry, content),
        )
    except sqlite3.OperationalError:
        pass


def get_config(name):
    try:
        row = _get_conn().execute(
            "SELECT content FROM config WHERE name=?", (name,)
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    return loads(row[0]) if row else None


def get_config_names():
    try:
        return [r[0] for r in _get_conn().execute("SELECT name FROM config")]
    except sqlite3.OperationalError:
        return []


def set_config(name, content):
    try:
        _get_conn().execute(
            "INSERT OR REPLACE INTO config VALUES (?, ?)",
            (name, dumps(content, indent=4)),
        )
    except sqlite3.OperationalError:
        pass


class ApiCallError(Exception):
    pass


class DiscoveryCache(object):
    _max_age = 60 * 60 * 24  # 1 day

    @staticmethod
    def get(url):
        cached = get_discovery_cache(url)
        if not cached:
            return None
        expiry_dt = datetime.strptime(cached["expiry"][:19], "%Y-%m-%dT%H:%M:%S")
        if expiry_dt < datetime.now():
            return None
        return cached["content"]

    @staticmethod
    def set(url, content):
        expiry = (
            datetime.now() + timedelta(seconds=DiscoveryCache._max_age)
        ).isoformat()[:19]
        set_discovery_cache(url, expiry, content)

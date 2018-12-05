import uuid
import json
import os

from functools import partial
from operator import itemgetter
from itertools import groupby
try:
    from itertools import ifilter
except ImportError:
    from builtins import filter as ifilter

try:
    import unicodecsv as csv
except ImportError:
    import csv

to_json = partial(json.dumps, indent=4, sort_keys=True)


CSV_OPTIONS = {"delimiter": ","}


def create_lumapps_uuid():  # type: () -> str
    """Generate a uid in the same format as lumapps

    Returns:
        A string valueof the unique id

    """
    return str(uuid.uuid4())


def set_new_lumapps_uuids(content):
    # type: (list[Dict[str]]) -> None
    """Generate a new unique id for every element in the list

    Args:
        content (list[Dict[str]]): the list of dict elements where to replace ids

    """
    with_uuid = list(nested_findall("uuid", content))
    for o in with_uuid:
        o["uuid"] = create_lumapps_uuid()


def nested_findall(key, dict_or_list):
    # type: (str, list[Dict[str | Dict | list]]) -> Generator[Dict[str]]

    """Find all elements by key recursively in lists or dictionnaries

    Args:
        key (str): The key to search
        dict_or_list (list[Dict[str or Dict or list]]): The dictionary/list of dictionaries to look into

    Yields:
        a generator where elements are elements of the dict with the searched key
    """

    if isinstance(dict_or_list, list):
        for d in dict_or_list:
            for element in nested_findall(key, d):
                yield element
    if isinstance(dict_or_list, dict):
        for k, v in dict_or_list.items():
            if key == k:
                yield dict_or_list
            elif isinstance(v, dict):
                for element in nested_findall(key, v):
                    yield element
            elif isinstance(v, list):
                for d in v:
                    for element in nested_findall(key, d):
                        yield element


def nested_find_one(key, value, dict_or_list):
    # type: (str, str,  list[Dict[str]]) -> (str,str)
    """Find the first element by key recursively in lists or dictionnaries

    Args:
        key (str): The key to search
        value (str): the value to search
        dict_or_list (list[Dict[str]]): The dictionary/list of dictionaries to look into

    Yields:
        the first element found
    """
    for d in nested_findall_value(key, value, dict_or_list):
        return d


def nested_findall_value(key, value, dict_or_list):
    # type: (str, str,  list[Dict[str]]) -> Generator[Dict[str]]
    """Find the first element by key and elements recursively in lists or dictionnaries

    Args:
        key (str): The key to search.
        value (str): the value to search.
        dict_or_list (list[Dict[str]]): The dictionary/list of dictionaries to look into.

    Yields:
        a generator where elements of the dict with the searched key and value
    """

    if isinstance(dict_or_list, list):
        for d in dict_or_list:
            for element in nested_findall_value(key, value, d):
                yield element
    if isinstance(dict_or_list, dict):
        for k, v in dict_or_list.items():
            if key == k and v == value:
                yield dict_or_list
            elif isinstance(v, dict):
                for element in nested_findall_value(key, value, v):
                    yield element
            elif isinstance(v, list):
                for d in v:
                    for element in nested_findall_value(key, value, d):
                        yield element


def read_csv_data(path, group_by=None, filter_by=None):
    # type: (str, str, Tuple[str,str]) -> Generator[Dict[str]]
    """

     Args:
        path (str): the path of the file to read
        group_by (str): the key to use to group the parsed csv
        filter_by (str, str): (key, value) filter only rows where key=value

    Yields:
        the rows parsed
    """
    if os.path.isfile(path):

        data = csv.DictReader(open(path), **CSV_OPTIONS)

        if filter_by is not None:
            (k, v) = filter_by
            yield ifilter(lambda e: e[k] == v, data)

        elif group_by is not None:
            for _, g in groupby(data, key=itemgetter(group_by)):
                yield list(g)

        else:
            yield (n for n in data)

from copy import deepcopy
from uuid import uuid4


def content_is_community(content):
    return isinstance(content, dict) and content.get("type") == "community"


def content_is_template(content):
    return "template" not in content


def get_components(content):
    if content_is_template(content):
        return content.get("components", [])
    else:
        return content.get("template").get("components", [])


def iter_widgets(container, **params):
    def widget_matches(w):
        match = True
        for k, v in params.items():
            match = match and w.get(k) == v
        return match

    if content_is_community(container):
        for templ in container.get("templates", []):
            for o2, container2 in iter_widgets(templ, **params):
                yield o2, container2
        return
    elif isinstance(container, dict):
        container = get_components(container)
    for o in container:
        if o.get("type") == "widget":
            if not widget_matches(o):
                continue
            yield o, container
            continue
        for o2, container2 in iter_widgets(
            o.get("components", o.get("cells", [])), **params
        ):
            yield o2, container2


def find_widget(container, **params):
    for w, _ in iter_widgets(container, **params):
        return w


def find_all_widgets(container, **params):
    return list(w for w, _ in iter_widgets(container, **params))


def find_widget_and_container(container, **params):
    for w, c in iter_widgets(container, **params):
        return w, c
    return None, None


def find_all_widgets_and_containers(container, **params):
    return list(((w, c) for w, c in iter_widgets(container, **params)))


def iter_with_key(dict_or_list, key):
    if isinstance(dict_or_list, list):
        for list_item in dict_or_list:
            for dict_match in iter_with_key(list_item, key):
                yield dict_match
    if isinstance(dict_or_list, dict):
        for k, v in dict_or_list.items():
            if key == k:
                yield dict_or_list
            elif isinstance(v, dict):
                for dict_match in iter_with_key(v, key):
                    yield dict_match
            elif isinstance(v, list):
                for list_item in v:
                    for dict_match in iter_with_key(list_item, key):
                        yield dict_match


def find_one_with_key_value(dict_or_list, key, value):
    for d in iter_with_key_value(dict_or_list, key, value):
        return d


def iter_with_key_value(dict_or_list, key, value):
    if isinstance(dict_or_list, list):
        for list_item in dict_or_list:
            for dict_match in iter_with_key_value(list_item, key, value):
                yield dict_match
    if isinstance(dict_or_list, dict):
        for k, v in dict_or_list.items():
            if key == k and v == value:
                yield dict_or_list
            elif isinstance(v, dict):
                for dict_match in iter_with_key_value(v, key, value):
                    yield dict_match
            elif isinstance(v, list):
                for list_item in v:
                    for dict_match in iter_with_key_value(list_item, key, value):
                        yield dict_match


def new_lumapps_uuid():
    return str(uuid4())


def set_new_lumapps_uuids(content):
    for o in list(iter_with_key(content, "uuid")):
        o["uuid"] = new_lumapps_uuid()


def copy_with_new_lumapps_uuids(content):
    new_content = deepcopy(content)
    set_new_lumapps_uuids(new_content)
    return new_content


def replace_matching_key_val(content, key, old_val, new_val):
    for d in iter_with_key(content, key):
        if d[key] == old_val:
            d[key] = new_val
        elif isinstance(d[key], list) and old_val in d[key]:
            d[key] = [i if i != old_val else new_val for i in d[key]]

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


def iter_with_key(key, dict_or_list):
    if isinstance(dict_or_list, list):
        for d in dict_or_list:
            for foo in iter_with_key(key, d):
                yield foo
    if isinstance(dict_or_list, dict):
        for k, v in dict_or_list.items():
            if key == k:
                yield dict_or_list
                break
            elif isinstance(v, dict):
                for foo in iter_with_key(key, v):
                    yield foo
            elif isinstance(v, list):
                for d in v:
                    for foo in iter_with_key(key, d):
                        yield foo


def find_one_with_key_value(key, value, dict_or_list):
    for d in iter_with_key_value(key, value, dict_or_list):
        return d


def iter_with_key_value(key, value, dict_or_list):
    if isinstance(dict_or_list, list):
        for d in dict_or_list:
            for foo in iter_with_key_value(key, value, d):
                yield foo
    if isinstance(dict_or_list, dict):
        for k, v in dict_or_list.items():
            if key == k and v == value:
                yield dict_or_list
                break
            elif isinstance(v, dict):
                for foo in iter_with_key_value(key, value, v):
                    yield foo
            elif isinstance(v, list):
                for d in v:
                    for foo in iter_with_key_value(key, value, d):
                        yield foo


def new_lumapps_uuid():
    return str(uuid4())


def set_new_lumapps_uuids(content):
    with_uuid = list(iter_with_key("uuid", content))
    for o in with_uuid:
        o["uuid"] = new_lumapps_uuid()


def copy_with_new_lumapps_uuids(content):
    new_content = deepcopy(content)
    set_new_lumapps_uuids(new_content)
    return new_content

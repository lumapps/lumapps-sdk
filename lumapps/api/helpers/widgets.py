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
    try:
        return next((w for w, _ in iter_widgets(container, **params)))
    except StopIteration:
        return None


def find_all_widgets(container, **params):
    return list(w for w, _ in iter_widgets(container, **params))


def find_widget_and_container(container, **params):
    try:
        return next(((w, c) for w, c in iter_widgets(container, **params)))
    except StopIteration:
        return None, None


def find_all_widgets_and_containers(container, **params):
    return list(((w, c) for w, c in iter_widgets(container, **params)))

import json

from lumapps.api.helpers import (
    find_all_widgets,
    find_widget,
    find_widget_and_container,
    find_all_widgets_and_containers,
    content_is_template,
    content_is_community,
)


def test_content_is_template():
    with open("tests/test_data/community_1.json") as fh:
        community = json.load(fh)
    assert content_is_template(community) is False
    with open("tests/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content_is_template(content) is False
    with open("tests/test_data/template_1.json") as fh:
        template = json.load(fh)
    assert content_is_template(template) is True


def test_content_is_community():
    with open("tests/test_data/community_1.json") as fh:
        community = json.load(fh)
    assert content_is_community(community) is True
    with open("tests/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content_is_community(content) is False
    with open("tests/test_data/template_1.json") as fh:
        template = json.load(fh)
    assert content_is_community(template) is False


def test_find_all_widgets_in_community():
    with open("tests/test_data/community_1.json") as fh:
        community = json.load(fh)
    assert community
    widgets = find_all_widgets(community, widgetType="html")
    assert len(widgets) == 0
    widgets = find_all_widgets(community, widgetType="meta-social")
    assert len(widgets) == 5


def test_find_all_widgets_in_content():
    with open("tests/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content
    widgets = find_all_widgets(content, widgetType="html")
    assert len(widgets) == 1


def test_find_all_widgets_in_template():
    with open("tests/test_data/template_1.json") as fh:
        template = json.load(fh)
    assert template
    widgets = find_all_widgets(template, widgetType="html")
    assert len(widgets) == 2


def test_find_widget():
    with open("tests/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content
    widget = find_widget(content, widgetType="foo")
    assert widget is None
    widget = find_widget(content, widgetType="html")
    assert isinstance(widget, dict)


def test_find_widget_and_container():
    with open("tests/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content
    widget, container = find_widget_and_container(content, widgetType="foo")
    assert widget is None
    assert container is None
    widget, container = find_widget_and_container(content, widgetType="html")
    assert isinstance(widget, dict)
    assert isinstance(container, list)


def test_find_all_widgets_and_containers():
    with open("tests/test_data/community_1.json") as fh:
        content = json.load(fh)
    assert content
    lst = find_all_widgets_and_containers(content, widgetType="foo")
    assert len(lst) == 0
    lst = find_all_widgets_and_containers(content, widgetType="meta-social")
    assert len(lst) == 5
    widget, container = lst[0]
    assert isinstance(widget, dict)
    assert isinstance(container, list)

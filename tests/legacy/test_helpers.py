import json
from uuid import UUID

from lumapps.api.helpers import (
    content_is_community,
    content_is_template,
    copy_with_new_lumapps_uuids,
    find_all_widgets,
    find_all_widgets_and_containers,
    find_one_with_key_value,
    find_widget,
    find_widget_and_container,
    iter_with_key,
    iter_with_key_value,
    new_lumapps_uuid,
    replace_key_val,
    set_new_lumapps_uuids,
)


def test_find_one_with_key_value():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    to_find = "2c2649f3-87de-46c6-bff3-ca3cbe3a8aa6"
    found = find_one_with_key_value(content, "uuid", to_find)
    assert found is not None


def test_content_is_template():
    with open("tests/legacy/test_data/community_1.json") as fh:
        community = json.load(fh)
    assert content_is_template(community) is False
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content_is_template(content) is False
    with open("tests/legacy/test_data/template_1.json") as fh:
        template = json.load(fh)
    assert content_is_template(template) is True


def test_content_is_community():
    with open("tests/legacy/test_data/community_1.json") as fh:
        community = json.load(fh)
    assert content_is_community(community) is True
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content_is_community(content) is False
    with open("tests/legacy/test_data/template_1.json") as fh:
        template = json.load(fh)
    assert content_is_community(template) is False


def test_find_all_widgets_in_community():
    with open("tests/legacy/test_data/community_1.json") as fh:
        community = json.load(fh)
    assert community
    widgets = find_all_widgets(community, widgetType="html")
    assert len(widgets) == 0
    widgets = find_all_widgets(community, widgetType="meta-social")
    assert len(widgets) == 5


def test_find_all_widgets_in_content():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content
    widgets = find_all_widgets(content, widgetType="html")
    assert len(widgets) == 1


def test_find_all_widgets_in_template():
    with open("tests/legacy/test_data/template_1.json") as fh:
        template = json.load(fh)
    assert template
    widgets = find_all_widgets(template, widgetType="html")
    assert len(widgets) == 2


def test_find_widget():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content
    widget = find_widget(content, widgetType="foo")
    assert widget is None
    widget = find_widget(content, widgetType="html")
    assert isinstance(widget, dict)


def test_find_widget_and_container():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    assert content
    widget, container = find_widget_and_container(content, widgetType="foo")
    assert widget is None
    assert container is None
    widget, container = find_widget_and_container(content, widgetType="html")
    assert isinstance(widget, dict)
    assert isinstance(container, list)


def test_find_all_widgets_and_containers():
    with open("tests/legacy/test_data/community_1.json") as fh:
        content = json.load(fh)
    assert content
    lst = find_all_widgets_and_containers(content, widgetType="foo")
    assert len(lst) == 0
    lst = find_all_widgets_and_containers(content, widgetType="meta-social")
    assert len(lst) == 5
    widget, container = lst[0]
    assert isinstance(widget, dict)
    assert isinstance(container, list)


def test_new_lumapps_uuid():
    new_uuid_str1 = new_lumapps_uuid()
    new_uuid_str2 = new_lumapps_uuid()
    assert isinstance(new_uuid_str1, str)
    assert new_uuid_str1 != new_uuid_str2
    uuid1 = UUID(new_uuid_str1)
    assert str(uuid1).lower() == new_uuid_str1


def test_iter_with_key_1():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    with_uuid = list(iter_with_key(content, "uuid"))
    assert len(with_uuid) == 4
    assert with_uuid[0]["uuid"] == "2c2649f3-87de-46c6-bff3-ca3cbe3a8aa6"
    assert with_uuid[1]["uuid"] == "2ad93c14-0a9d-4d0e-a91b-eb38e1025991"
    assert with_uuid[2]["uuid"] == "f0951e06-ffb6-4406-a9c5-97e0be977f94"
    assert with_uuid[3]["uuid"] == "ae9aac74-1ee5-45c2-9a57-8e447ad663f3"


def test_iter_with_key_2():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    matches = list(iter_with_key(content, "instance"))
    assert len(matches) == 3


def test_iter_with_key_3():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    matches = list(iter_with_key([content], "instance"))
    assert len(matches) == 3


def test_iter_with_key_value_1():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    with_uuid = list(iter_with_key_value(content, "uuid", "foo"))
    assert with_uuid == []
    with_uuid = list(
        iter_with_key_value(content, "uuid", "2c2649f3-87de-46c6-bff3-ca3cbe3a8aa6")
    )
    assert len(with_uuid) == 1


def test_iter_with_key_value_2():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    with_uuid = list(iter_with_key_value([content], "uuid", "foo"))
    assert with_uuid == []
    with_uuid = list(
        iter_with_key_value([content], "uuid", "2c2649f3-87de-46c6-bff3-ca3cbe3a8aa6")
    )
    assert len(with_uuid) == 1


def test_set_new_lumapps_uuids():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    set_new_lumapps_uuids(content)
    with_uuid = list(iter_with_key(content, "uuid"))
    assert len(with_uuid) == 4
    assert with_uuid[0]["uuid"] != "2c2649f3-87de-46c6-bff3-ca3cbe3a8aa6"
    assert with_uuid[1]["uuid"] != "2ad93c14-0a9d-4d0e-a91b-eb38e1025991"
    assert with_uuid[2]["uuid"] != "f0951e06-ffb6-4406-a9c5-97e0be977f94"
    assert with_uuid[3]["uuid"] != "ae9aac74-1ee5-45c2-9a57-8e447ad663f3"


def test_copy_with_new_lumapps_uuids():
    with open("tests/legacy/test_data/content_1.json") as fh:
        content = json.load(fh)
    content2 = copy_with_new_lumapps_uuids(content)
    assert content != content2
    with_uuid = list(iter_with_key(content, "uuid"))
    assert len(with_uuid) == 4
    assert with_uuid[0]["uuid"] == "2c2649f3-87de-46c6-bff3-ca3cbe3a8aa6"
    assert with_uuid[1]["uuid"] == "2ad93c14-0a9d-4d0e-a91b-eb38e1025991"
    assert with_uuid[2]["uuid"] == "f0951e06-ffb6-4406-a9c5-97e0be977f94"
    assert with_uuid[3]["uuid"] == "ae9aac74-1ee5-45c2-9a57-8e447ad663f3"
    with_uuid = list(iter_with_key(content2, "uuid"))
    assert len(with_uuid) == 4
    assert with_uuid[0]["uuid"] != "2c2649f3-87de-46c6-bff3-ca3cbe3a8aa6"
    assert with_uuid[1]["uuid"] != "2ad93c14-0a9d-4d0e-a91b-eb38e1025991"
    assert with_uuid[2]["uuid"] != "f0951e06-ffb6-4406-a9c5-97e0be977f94"
    assert with_uuid[3]["uuid"] != "ae9aac74-1ee5-45c2-9a57-8e447ad663f3"


def test_replace_key_val():
    with open("tests/legacy/test_data/community_1.json") as fh:
        c = json.load(fh)
    replace_key_val(c, "instance", "2222222222", "foo_bar_123")
    assert c["instance"] == "foo_bar_123"
    tmpl = c["template"]
    props = tmpl["components"][0]["cells"][0]["components"][0]["properties"]
    assert props["instance"] == ["foo_bar_123"]
    assert props["media"][0]["instance"] == "foo_bar_123"

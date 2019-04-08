import pytest
import json

from lumapps.helpers.media import uploaded_to_media
from lumapps.helpers.media import upload_and_save


def test_uploaded_to_media():
    # Test when name is given
    with open("test_data/uploaded_file.json", "r") as f:
        uploaded_file = json.load(f)
    lang = "en"
    instance = "20392"
    name = "test"
    media = uploaded_to_media(uploaded_file, instance, lang, name)
    assert media["content"][0]["value"] == uploaded_file["blobKey"]
    assert media["content"][0]["name"] == name
    assert media["content"][0]["lang"] == lang
    assert media["name"] == {lang: name}
    assert media["instance"] == instance

    # Test when name is not given
    media = uploaded_to_media(uploaded_file, instance, lang)
    assert media["content"][0]["value"] == uploaded_file["blobKey"]
    assert media["content"][0]["name"] == uploaded_file["name"]
    assert media["content"][0]["lang"] == lang
    assert media["name"] == {lang: uploaded_file["name"]}
    assert media["instance"] == instance

    # Test whith additionnal params
    key = "289830"
    media = uploaded_to_media(
        uploaded_file, instance, lang, hasCroppedContent=False, contentKey=key
    )
    assert media["hasCroppedContent"] is False
    assert media["contentKey"] == key


def test_parameters_length():
    # if optional parameters are specified (langs & names)
    # their length must be equal to the files list
    # raise an error if not
    files = ["fake_test_file_one", "fake_test_file_two"]
    langs = ["en", "fr"]
    names = ["first_fake", "second_fake"]
    partial_langs = ["en"]
    partial_names = ["first_fake"]
    client = instance = None

    with pytest.raises(ValueError):
        upload_and_save(client, instance, files, partial_langs, names)
    with pytest.raises(ValueError):
        upload_and_save(client, instance, files, langs, partial_names)

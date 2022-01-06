from lumapps.api.errors import get_http_err_content


def test_get_http_err_content():
    err = object()
    s1 = get_http_err_content(err)
    assert s1 == ""

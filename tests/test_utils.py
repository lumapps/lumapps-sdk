from lumapps.api.utils import list_prune_filters


def test_list_prune_filters(capsys):
    list_prune_filters()
    captured = capsys.readouterr()
    assert captured.out.startswith("PRUNE FILTERS:")

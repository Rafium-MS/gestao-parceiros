from version import get_version_string, get_version_info


def test_get_version_string():
    assert get_version_string() == "1.1.1"


def test_get_version_info():
    info = get_version_info()
    assert info["full"] == "1.1.1"
    assert info["major"] == 1
    assert info["minor"] == 1
    assert info["patch"] == 1
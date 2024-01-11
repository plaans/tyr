import pytest


def assert_dicts_equal(dict1: dict, dict2: dict) -> None:
    """Asserts the two dictionaries are equal."""
    common_items = {
        key: value
        for key, value in dict1.items()
        if key in dict2 and dict2[key] == value
    }

    diff_items = {
        key: (dict1[key], dict2[key])
        for key in dict1.keys() & dict2.keys()
        if dict1[key] != dict2[key]
    }
    diff_items.update(
        {key: (value, None) for key, value in dict1.items() if key not in dict2}
    )
    diff_items.update(
        {key: (None, value) for key, value in dict2.items() if key not in dict1}
    )

    def fmt(d: dict) -> str:
        return "\n".join(map(lambda i: "\t" + ": ".join(map(str, i)), d.items()))

    assert_msg = f"""{dict1} == {dict2}
Common items:
{fmt(common_items)}
Differing items:
{fmt(diff_items)}
"""

    assert dict1 == dict2, assert_msg  # nosec: B101


def assert_is_abstract(builder):
    """Asserts the given class cannot be instantiated."""
    with pytest.raises(TypeError):
        builder()


def assert_is_not_abstract(builder):
    """Asserts the given class can be instantiated."""
    builder()


def assert_is_singleton(builder):
    """Asserts the given class is a singleton."""
    instance1 = builder()
    instance2 = builder()
    assert instance1 is instance2  # nosec: B101

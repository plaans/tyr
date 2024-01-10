import pytest


def assert_is_abstract(cls, *args, **kwargs):
    """Asserts the given class cannot be instantiated."""
    with pytest.raises(TypeError):
        cls(*args, **kwargs)


def assert_is_not_abstract(cls, *args, **kwargs):
    """Asserts the given class can be instantiated."""
    cls(*args, **kwargs)

from typing import TypeVar

from tests.utils.asserts import assert_is_singleton
from tests.utils.gen.model import ModelTest

T = TypeVar("T")


# pylint: disable = abstract-method
class SingletonModelTest(ModelTest[T]):
    """Represents a test bench on a singleton model class."""

    def test_is_singleton(self):
        """Asserts that the class is a singleton."""
        assert_is_singleton(self.get_instance)

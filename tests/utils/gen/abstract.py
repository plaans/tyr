from typing import TypeVar

from tests.utils.asserts import assert_is_abstract, assert_is_not_abstract
from tests.utils.gen.model import ModelTest

T = TypeVar("T")


class AbstractModelTest(ModelTest[T]):
    """Represents a test bench on an abstract model class."""

    # ================================== Getters ================================= #

    def get_abstract_instance(self) -> T:
        """
        Returns:
            T: The base abstract instance of the class to test.
        """
        raise NotImplementedError()

    # =================================== Tests ================================== #

    def test_is_abstract(self):
        """Asserts that the class is abstract."""
        assert_is_abstract(self.get_abstract_instance)
        assert_is_not_abstract(self.get_instance)

import re
from typing import Any, Dict, Generic, TypeVar

from tests.utils.asserts import assert_dicts_equal

T = TypeVar("T")


class ModelTest(Generic[T]):
    """Represents a test bench on a model class."""

    # ================================== Getters ================================= #

    def get_default_attributes(self) -> Dict[str, Any]:
        """
        Returns:
            Dict[str, Any]: The default value of the instance's attributes.
        """
        raise NotImplementedError()

    def get_instance(self) -> T:
        """
        Returns:
            T: Returns a new instance of the object.
        """
        raise NotImplementedError

    # =================================== Tests ================================== #

    def test_default_attributes(self):
        """Asserts the default value of the given class' attributes are the correct ones."""
        attributes = self.get_instance().__dict__
        expected = self.get_default_attributes()
        assert_dicts_equal(attributes, expected)

    def test_getters(self):
        """
        Asserts the getters of the given class returns the associated protected attribute
        and each protected attribute has an associated getter.
        """
        attributes = self.get_instance().__dict__
        for attribute, expected in attributes.items():
            getter = re.sub("^_", "", attribute)
            result = getattr(self.get_instance(), getter)
            assert_msg = f"assert[getter={getter}] {result} == {expected}"
            assert result == expected, assert_msg  # nosec: B101

from typing import TypeVar

from tests.utils.gen.abstract import AbstractModelTest
from tests.utils.gen.singleton import SingletonModelTest

T = TypeVar("T")


# pylint: disable = abstract-method
class AbstractSingletonModelTest(AbstractModelTest[T], SingletonModelTest[T]):
    """Represents a test bench on an abstract singleton model class."""

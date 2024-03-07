from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class Lazy(Generic[T]):
    """A wrapper to make a value lazy."""

    def __init__(self, value_factory: Callable[[], T]) -> None:
        self._value_factory = value_factory
        self._value: Optional[T] = None

    @property
    def value(self) -> T:
        """
        Returns:
            T: The value of the lazy object.
        """
        if self._value is None:
            self._value = self.value_factory()
        return self._value

    @property
    def value_factory(self) -> Callable[[], T]:
        """
        Returns:
            Callable[[], T]: The callback to use to build the value.
        """
        return self._value_factory


__all__ = ["Lazy"]

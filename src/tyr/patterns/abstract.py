from typing import Any


class AbstractMeta(type):
    """An abstract class which cannot be instantiated but its children can."""

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if cls is Abstract or Abstract in cls.__bases__:
            raise TypeError(f"Abstract class {cls.__name__} cannot be instantiated")
        return super().__call__(*args, **kwds)


# pylint: disable = too-few-public-methods
class Abstract(metaclass=AbstractMeta):
    """An abstract class which cannot be instantiated but its children can."""

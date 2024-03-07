from . import abstract, lazy, singleton
from .abstract import *
from .lazy import *
from .singleton import *


class AbstractSingletonMeta(abstract.AbstractMeta, singleton.SingletonMeta):
    """An abstract thread-safe singleton which cannot be instantiated but its children can."""


__all__ = (
    abstract.__all__ + lazy.__all__ + singleton.__all__ + ["AbstractSingletonMeta"]
)

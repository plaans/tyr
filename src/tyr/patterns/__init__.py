from . import abstract as a
from . import singleton as s
from .abstract import Abstract
from .singleton import Singleton


class AbstractSingletonMeta(a.AbstractMeta, s.SingletonMeta):
    """An abstract thread-safe singleton which cannot be instantiated but its children can."""

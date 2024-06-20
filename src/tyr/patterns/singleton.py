from threading import Lock


class SingletonMeta(type):
    """A thread-safe implementation of Singleton."""

    _instances: dict = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        created = False
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
                created = True
        if created and hasattr(instance, "__post_init__"):
            instance.__post_init__(*args, **kwargs)
        return cls._instances[cls]

    def clear_singleton(cls) -> None:
        """
        Clears the instance of the singleton class.
        """
        with cls._lock:
            if cls in cls._instances:
                del cls._instances[cls]

    def purge_singletons(cls) -> None:
        """
        Clears all instances of all singleton classes.
        """
        with cls._lock:
            cls._instances.clear()


# pylint: disable = too-few-public-methods
class Singleton(metaclass=SingletonMeta):
    """A thread-safe implementation of Singleton."""


__all__ = ["Singleton"]

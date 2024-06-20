from threading import Thread

import pytest

from tests.utils.asserts import assert_is_singleton
from tyr import Singleton


class ChildSingleton(Singleton):
    pass


class TestSingleton:
    @pytest.mark.parametrize("klass", [Singleton, ChildSingleton])
    def test_singlethread_singleton(self, klass):
        assert_is_singleton(klass)

    @pytest.mark.parametrize("klass", [Singleton, ChildSingleton])
    def test_multithread_singleton(self, klass):
        instances = set()
        num_threads = 10

        def get_instance():
            instance = klass()
            instances.add(instance)

        threads = [Thread(target=get_instance) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(instances) == 1

    def test_inheritance_singleton(self):
        base = Singleton()
        child = ChildSingleton()
        assert base is not child

    def test_post_init(self):
        class SingletonWithPostInit(Singleton):
            def __init__(self) -> None:
                super().__init__()
                self.counter = 0

            def __post_init__(self):
                self.counter += 1

        singleton = [SingletonWithPostInit() for _ in range(10)][0]
        assert singleton.counter == 1

    def test_clear_singleton(self):
        Singleton.purge_singletons()
        instance = Singleton()
        assert Singleton._instances == {Singleton: instance}
        Singleton.clear_singleton()
        assert Singleton._instances == {}

    def test_purge_singletons(self):
        Singleton()
        assert Singleton._instances != {}
        Singleton.purge_singletons()
        assert Singleton._instances == {}

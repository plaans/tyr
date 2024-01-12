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

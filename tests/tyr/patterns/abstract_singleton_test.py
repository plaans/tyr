from tests.utils.asserts import (
    assert_is_abstract,
    assert_is_not_abstract,
    assert_is_singleton,
)
from tyr import Abstract, AbstractSingletonMeta, Singleton


class ChildA(Abstract, Singleton, metaclass=AbstractSingletonMeta):
    pass


class ChildB(ChildA):
    pass


class TestAbstractSingleton:
    def test_child_instantiation_raises_error(self):
        assert_is_abstract(ChildA)

    def test_subchild_instantiation_is_ok(self):
        assert_is_not_abstract(ChildB)

    def test_is_singleton(self):
        assert_is_singleton(ChildB)

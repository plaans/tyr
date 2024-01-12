from tests.utils.asserts import assert_is_abstract, assert_is_not_abstract
from tyr import Abstract


class ChildA(Abstract):
    pass


class ChildB(ChildA):
    pass


class TestAbstract:
    def test_instantiation_raises_error(self):
        assert_is_abstract(Abstract)

    def test_child_instantiation_raises_error(self):
        assert_is_abstract(ChildA)

    def test_subchild_instantiation_is_ok(self):
        assert_is_not_abstract(ChildB)

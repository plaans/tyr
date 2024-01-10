import pytest

from tyr import Abstract


class ChildA(Abstract):
    pass


class ChildB(ChildA):
    pass


class TestAbstract:
    def test_instantiation_raises_error(self):
        with pytest.raises(TypeError):
            Abstract()

    def test_child_instantiation_raises_error(self):
        with pytest.raises(TypeError):
            ChildA()

    def test_subchild_instantiation_is_ok(self):
        ChildB()

from tyr import Lazy


class TestLazy:
    def test_lazy_initialization(self):
        called = 0
        value = "Init Value"

        def init_callback():
            nonlocal called
            called = called + 1
            return value

        lazy = Lazy(init_callback)
        assert lazy._value is None
        assert called == 0
        assert lazy.value == value
        assert called == 1
        assert lazy._value == value
        assert called == 1
        assert lazy.value == value
        assert called == 1

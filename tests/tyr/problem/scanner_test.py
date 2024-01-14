from unittest.mock import patch

import tests.integration.problem as problem_module
from tests.integration.problem.domains import FakeDomain
from tyr.problem import get_all_domains


class TestUtils:
    @patch("tyr.problem")
    def test_get_all_domains_mocked(self, mocked_module):
        mocked_module.__path__ = problem_module.__path__
        mocked_module.__name__ = problem_module.__name__
        result = get_all_domains()
        expected = [FakeDomain()]
        assert result == expected

    def test_get_all_domains_real(self):
        # Check no crash
        get_all_domains()

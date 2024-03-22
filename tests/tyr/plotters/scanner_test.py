from unittest.mock import patch

import tests.integration.plotters as metric_module
from tests.integration.plotters.plotters import FakePlotter
from tyr.plotters.scanner import get_all_plotters


class TestUtils:
    @patch("tyr.plotters.plotters")
    def test_get_all_domains_mocked(self, mocked_module):
        mocked_module.__path__ = metric_module.__path__
        mocked_module.__name__ = metric_module.__name__
        result = get_all_plotters()
        expected = [FakePlotter()]
        assert result == expected

    def test_get_all_domains_real(self):
        # Check no crash
        get_all_plotters()

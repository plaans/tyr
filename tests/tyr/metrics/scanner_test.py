from unittest.mock import patch

import tests.integration.metrics as metric_module
from tests.integration.metrics.metrics import FakeMetric
from tyr.metrics.scanner import get_all_metrics


class TestUtils:
    @patch("tyr.metrics.metrics")
    def test_get_all_domains_mocked(self, mocked_module):
        mocked_module.__path__ = metric_module.__path__
        mocked_module.__name__ = metric_module.__name__
        result = get_all_metrics()
        expected = [FakeMetric()]
        assert result == expected

    def test_get_all_domains_real(self):
        # Check no crash
        get_all_metrics()

from tyr.metrics.metric import Metric


# pylint: disable=too-few-public-methods
class FakeMetric(Metric):
    """A fake metric to test the Metric class."""

    def _evaluate(self, results, all_results):
        """Fake evaluate method."""

from math import log10
from tyr.metrics.metric import Metric
from tyr.planners.model.result import PlannerResultStatus


class AgileScoreMetric(Metric):
    """A metric to evaluate the agile score of a planner."""

    def evaluate(self, results):
        """Evaluate the performance of a planner."""
        if len(results) == 0:
            return 0

        total = 0
        for result in results:
            computation_time = result.computation_time
            timeout = result.config.timeout
            if result.status != PlannerResultStatus.SOLVED:
                total += 0
            elif computation_time < 1:
                total += 1
            elif computation_time > timeout:
                total += 0
            else:
                total += 1 - log10(computation_time) / log10(timeout)
        return total / len(results)


__all__ = ["AgileScoreMetric"]

from tyr.planners.model.singulatiry_planner import SingularityPlanner


# pylint: disable=too-many-ancestors
class LinearPlanner(SingularityPlanner):
    """The Linear planner wrapped into local singularity planner."""

    def _file_extension(self) -> str:
        return "hddl"

    def _get_singularity_file_name(self) -> str:
        return "config-sat-1.sif"


class LinearExponentialPlanner(LinearPlanner):
    """The Linear planner configured to use exponential version of some problems."""


class LinearLinearPlanner(LinearPlanner):
    """The Linear planner configured to use linear version of some problems."""


class LinearInsertionPlanner(LinearPlanner):
    """The Linear planner configured to use task insertion version of some problems."""


__all__ = ["LinearPlanner", "LinearInsertionPlanner", "LinearLinearPlanner"]

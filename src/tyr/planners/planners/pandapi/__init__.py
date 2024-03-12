from tyr.planners.model.singulatiry_planner import SingularityPlanner


# pylint: disable=too-many-ancestors
class PandaPiPlanner(SingularityPlanner):
    """The PandaPi planner wrapped into local singularity planner."""

    def _file_extension(self) -> str:
        return "hddl"

    def _get_singularity_file_name(self) -> str:
        return "ppro-po-sat-gas-ff.sif"


class PandaPiExponentialPlanner(PandaPiPlanner):
    """The PandaPi planner configured to use exponential version of some problems."""


class PandaPiLinearPlanner(PandaPiPlanner):
    """The PandaPi planner configured to use linear version of some problems."""


class PandaPiInsertionPlanner(PandaPiPlanner):
    """The PandaPi planner configured to use task insertion version of some problems."""


__all__ = ["PandaPiPlanner", "PandaPiInsertionPlanner", "PandaPiLinearPlanner"]

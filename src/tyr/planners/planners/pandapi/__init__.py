from tyr.planners.model.apptainer_planner import ApptainerPlanner


# pylint: disable=too-many-ancestors
class PandaPiPlanner(ApptainerPlanner):
    """The PandaPi planner wrapped into local apptainer planner."""

    def _file_extension(self) -> str:
        return "hddl"

    def _get_apptainer_file_name(self) -> str:
        return "ppro-po-sat-gas-ff.sif"


class PandaPiExponentialPlanner(PandaPiPlanner):
    """The PandaPi planner configured to use exponential version of some problems."""


class PandaPiLinearPlanner(PandaPiPlanner):
    """The PandaPi planner configured to use linear version of some problems."""


class PandaPiInsertionPlanner(PandaPiPlanner):
    """The PandaPi planner configured to use task insertion version of some problems."""


__all__ = [
    "PandaPiPlanner",
    "PandaPiExponentialPlanner",
    "PandaPiInsertionPlanner",
    "PandaPiLinearPlanner",
]

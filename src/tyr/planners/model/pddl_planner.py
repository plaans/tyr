import re

from unified_planning.engines import PDDLPlanner
from unified_planning.environment import get_environment
from unified_planning.shortcuts import ProblemKind


class TyrPDDLPlanner(PDDLPlanner):
    """A local wrapper from unified planning PDDL Planner."""

    @classmethod
    def _get_name(cls) -> str:
        return re.sub(r"([A-Z])", r"-\1", cls.__name__[:-7]).lower().lstrip("-")

    @classmethod
    def register(cls):
        """Registers the planner into unified planning."""
        env = get_environment()
        env.factory.add_engine(cls._get_name(), cls.__module__, cls.__name__)

    @property
    def name(self):
        return self._get_name()

    @staticmethod
    def supported_kind() -> ProblemKind:
        raise NotImplementedError()

    @staticmethod
    def supports(_) -> bool:
        return True

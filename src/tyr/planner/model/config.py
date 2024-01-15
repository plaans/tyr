from typing import Any, Dict


class PlannerConfig:
    """Represents the configuration of a planner."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self._name = config["name"]
        self._problems = config["problems"]

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the planner.
        """
        return self._name

    @property
    def problems(self) -> Dict[str, str]:
        """
        Returns:
            Dict[str, str]: A map from a domain name to a version name.
        """
        return self._problems

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlannerConfig):
            return False
        return self.__dict__ == other.__dict__

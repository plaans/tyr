from typing import TYPE_CHECKING, Dict

from unified_planning.shortcuts import AbstractProblem

from tyr.patterns import Lazy

if TYPE_CHECKING:
    from tyr.problem.model.domain import AbstractDomain


class ProblemInstance:
    """
    Represents an internal problem to solve.

    It is made of different versions allowing to make the problem compatible for different planners.
    The value of this versions are lazy, so the unified planning problem is only build when needed.
    """

    def __init__(self, domain: "AbstractDomain", uid: str) -> None:
        self._uid = uid
        self._domain = domain
        self._versions: Dict[str, Lazy[AbstractProblem]] = {}

    @property
    def uid(self) -> str:
        """
        Returns:
            str: The id of the problem.
        """
        return self._uid

    @property
    def domain(self) -> "AbstractDomain":
        """
        Returns:
            AbstractDomain: The domain of the problem.
        """
        return self._domain

    @property
    def versions(self) -> Dict[str, Lazy[AbstractProblem]]:
        """
        Returns:
            Dict[str, Lazy[AbstractProblem]]: The unified planning problems indexed by version name.
        """
        return self._versions

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the problem.
        """
        return f"{self.domain.name}:{self.uid}"

    @property
    def is_empty(self) -> bool:
        """
        Returns:
            bool: Whether the problem has no versions.
        """
        return len(self.versions) == 0

    def add_version(self, version_name: str, version: Lazy[AbstractProblem]) -> None:
        """Adds a new version to the problem.

        NOTE: There is no security about overriding an existing version.

        Args:
            version_name (str): The name of the version to add.
            version (Lazy[AbstractProblem]): The lazy value of the problem version.
        """
        self._versions[version_name] = version

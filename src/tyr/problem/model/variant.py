import functools
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.patterns import Abstract, Lazy
from tyr.problem.model.instance import ProblemInstance

if TYPE_CHECKING:
    from tyr.problem.model.domain import AbstractDomain


class AbstractVariant(Abstract):
    """
    Represents the base class for all variants.

    The constructor needs a `problem_hydrator`.
    It is a function hydrating a problem based on its uid for this variant.

    All the generated problems are saved in cache.
    The cache lives while the variant's domain lives.
    """

    def __init__(
        self,
        domain: "AbstractDomain",
        problem_factories: List[Callable[[str], Optional[AbstractProblem]]],
    ) -> None:
        super().__init__()
        self._name = self.__class__.__name__[:-7].lower()
        self._problem_factories = problem_factories
        self._domain = domain
        self._problems: Dict[str, ProblemInstance] = {}

    @property
    def problem_factories(self) -> List[Callable[[str], Optional[AbstractProblem]]]:
        """
        Returns:
            List[Callable[[str], Optional[AbstractProblem]]]: The functions to build new problems.
        """
        return self._problem_factories

    @property
    def domain(self) -> "AbstractDomain":
        """
        Returns:
            AbstractDomain: The domain of the variant.
        """
        return self._domain

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the variant.
        """
        return self._name

    @property
    def problems(self) -> Dict[str, ProblemInstance]:
        """
        Returns:
            Dict[str, Problem]: The problems of the domain, indexed by id.
        """
        return self._problems

    def build_problem(self, problem_id: str) -> ProblemInstance:
        """
        Builds the problem with the given if.
        If no problem is associated with the given id, nothing is built.

        Args:
            problem (Problem): The problem to hydrate.
        """
        problem = ProblemInstance(self, problem_id)
        for factory in self.problem_factories:
            version_name = factory.__name__[factory.__name__.find("problem_") + 8 :]
            problem.add_version(
                version_name,
                Lazy(functools.partial(factory, problem)),
            )
        return problem

    def get_problem_from_cache(self, problem_id: str) -> Optional[ProblemInstance]:
        """Tries to load the problem with the given id from the cache.

        Args:
            problem_id (str): The id of the problem to retreive.

        Returns:
            Optional[ProblemInstance]: The cached problem or `None` if the problem is not present.
        """
        return self._problems.get(problem_id, None)

    def get_problem(self, problem_id: str) -> Optional[ProblemInstance]:
        """
        Loads the problem with the given id from the cache.
        If there is no result, builds it from the problem factory.
        Finally, saves the result to the cache before returning it.

        Args:
            problem_id (str): The of of the requested problem.

        Returns:
            Optional[ProblemInstance]: The requested problem or `None` if it does not exist.
        """
        problem = self.get_problem_from_cache(problem_id)
        if problem is None:
            problem = self.build_problem(problem_id)
        if problem.is_empty:
            return None
        self.save_problem_to_cache(problem)
        return problem

    def save_problem_to_cache(self, problem: Optional[ProblemInstance]) -> None:
        """
        Saves the given problem to the cache.
        Does nothing if the problem is `None`.

        Args:
            problem (Optional[ProblemInstance]): The problem to save.
        """
        if problem is not None:
            self._problems[problem.uid] = problem

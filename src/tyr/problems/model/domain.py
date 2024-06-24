import functools
import re
from pathlib import Path
from typing import Dict, List, Optional

from unified_planning.io import PDDLReader
from unified_planning.plans import Plan
from unified_planning.shortcuts import AbstractProblem

from tyr.patterns import Abstract, AbstractSingletonMeta, Lazy, Singleton
from tyr.problems.model.instance import ProblemInstance


class AbstractDomain(Abstract, Singleton, metaclass=AbstractSingletonMeta):
    """
    Represents the base class for all domains.

    For each problem version, the class must implements the method
    ``` python
    def build_problem_VERSION(self, problem_id: int) -> Optional[up.AbstractProblem]
    ```
    """

    def __init__(self) -> None:
        super().__init__()
        base_name = self.__class__.__name__[:-6]
        self._name = re.sub(r"([A-Z])", r"-\1", base_name).lower().lstrip("-")
        self._problems: Dict[int, ProblemInstance] = {}

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the domain.
        """
        return self._name

    @property
    def problems(self) -> Dict[int, ProblemInstance]:
        """
        Returns:
            Dict[int, ProblemInstance]: The problems of the domain, indexed by id.
        """
        return self._problems

    def get_num_problems(self) -> int:
        """
        Returns:
            int: The number of problems present in the domain.
        """
        raise NotImplementedError()

    def get_versions(self) -> List[str]:
        """
        Returns:
            List[str]: The list of available versions.
        """
        return [v[14:] for v in dir(self) if v.startswith("build_problem_")]

    def build_problem(self, problem_id: int) -> Optional[ProblemInstance]:
        """Builds the problem with the given id.

        Args:
            problem_id (int): The id of the problem to create.

        Returns:
            Optional[ProblemInstance]: The generated problem, `None` if it doesn't exist.
        """
        problem_factories = [
            getattr(self, v) for v in dir(self) if v.startswith("build_problem_")
        ]
        if len(problem_factories) == 0:
            print(f"[WARN] Cannot find problem builders for domain {self.name}")
            return None

        problem = ProblemInstance(self, problem_id)
        for factory in problem_factories:
            version_name = factory.__name__[factory.__name__.find("problem_") + 8 :]
            problem.add_version(version_name, Lazy(functools.partial(factory, problem)))

        return problem

    def get_problem(self, problem_id: int) -> Optional[ProblemInstance]:
        """Builds the problem with the given id.

        Args:
            problem_id (int): The id of the problem to build.

        Returns:
            Optional[ProblemInstance]: The generated problem or `None` if the problem doesn't exist.
        """
        problem = self.load_problem_from_cache(problem_id)
        if problem is None:
            problem = self.build_problem(problem_id)
        self.save_problem_to_cache(problem)
        return problem

    def get_problem_version(
        self,
        problem_id: int,
        version: str,
    ) -> Optional[AbstractProblem]:
        """Retrieves the requested version with the given id.

        Args:
            problem_id (int): The id of the problem to search.
            version (str): The requested version of the problem.

        Returns:
            Optional[AbstractProblem]: The value of the requested version.
                `None` if the problem or the version doee not exist.
        """
        problem = self.get_problem(problem_id)
        if problem is None:
            return None
        try:
            return problem.versions[version].value
        except KeyError:
            return None

    # pylint: disable = unused-argument
    def get_quality_of_plan(
        self, plan: Plan, version: AbstractProblem
    ) -> Optional[float]:
        """Extracts the quality of the given plan.

        Args:
            plan (Plan): The plan to study.
            version (AbstractProblem): The version of the problem used to generate the plan.

        Returns:
            Optional[float]: The quality of the plan if any.
        """
        return None

    def load_problem_from_cache(self, problem_id: int) -> Optional[AbstractProblem]:
        """Loads the problem with the given id from the cache.

        Args:
            problem_id (int): The id of the problem to load

        Returns:
            Optional[AbstractProblem]: The cached problem or `None`.
        """
        return self.problems.get(problem_id, None)

    def load_from_files(
        self,
        folder_path: Path,
        problem_id: int,
    ) -> Optional[AbstractProblem]:
        """
        Builds a unified planning problem based on the files present on the given folder.

        The folder must have one file starting with "domain" which represents the domain.
        It also must have one file starting with "instance-ID" which represents the instance.

        Args:
            folder_path (Path): The path of the folder to use to find the files.
            problem_id (int): The uid of the problem to load.

        Returns:
            Optional[AbstractProblem]: The optional problem. `None` if no files found.
        """
        folder_path = folder_path.resolve()

        domain_file, problem_file = None, None
        for file in folder_path.iterdir():
            if file.name.startswith("domain"):
                domain_file = file
            if file.name.startswith(f"instance-{problem_id}"):
                problem_file = file

        if domain_file is None or problem_file is None:
            return None

        return PDDLReader().parse_problem(
            domain_file.as_posix(),
            problem_file.as_posix(),
        )

    def save_problem_to_cache(self, problem: Optional[ProblemInstance]) -> None:
        """
        Saves the given problem to the cache.
        Does nothing if it is `None`.

        Args:
            problem (Optional[ProblemInstance]): The optional problem to save.
        """
        if problem is not None:
            self.problems[problem.uid] = problem


__all__ = ["AbstractDomain"]

import functools
from pathlib import Path
from typing import Dict, Optional

from unified_planning.io import PDDLReader
from unified_planning.shortcuts import AbstractProblem

from tyr.patterns import Abstract, AbstractSingletonMeta, Lazy, Singleton
from tyr.problem.model.instance import ProblemInstance


class AbstractDomain(Abstract, Singleton, metaclass=AbstractSingletonMeta):
    """
    Represents the base class for all domains.

    For each problem version, the class must implements the method
    ``` python
    def build_problem_VERSION(self, problem_id: str) -> Optional[up.AbstractProblem]
    ```
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = self.__class__.__name__[:-6].lower()
        self._problems: Dict[str, ProblemInstance] = {}

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the domain.
        """
        return self._name

    @property
    def problems(self) -> Dict[str, ProblemInstance]:
        """
        Returns:
            Dict[str, ProblemInstance]: The problems of the domain, indexed by id.
        """
        return self._problems

    def build_problem(self, problem_id: str) -> Optional[ProblemInstance]:
        """Builds the problem with the given id.

        Args:
            problem_id (str): The id of the problem to create.

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

    def get_problem(self, problem_id: str) -> Optional[ProblemInstance]:
        """Builds the problem with the given id.

        Args:
            problem_id (str): The id of the problem to build.

        Returns:
            Optional[ProblemInstance]: The generated problem or `None` if the problem doesn't exist.
        """
        problem = self.load_problem_from_cache(problem_id)
        if problem is None:
            problem = self.build_problem(problem_id)
        self.save_problem_to_cache(problem)
        return problem

    def load_problem_from_cache(self, problem_id: str) -> Optional[AbstractProblem]:
        """Loads the problem with the given id from the cache.

        Args:
            problem_id (str): The id of the problem to load

        Returns:
            Optional[AbstractProblem]: The cached problem or `None`.
        """
        return self.problems.get(problem_id, None)

    def load_from_files(
        self,
        folder_path: Path,
        problem_id: str,
    ) -> Optional[AbstractProblem]:
        """
        Builds a unified planning problem based on the files present on the given folder.

        The folder must have one file starting with "domain" which represents the domain.
        It also must have one file starting with "instance-ID" which represents the instance.

        Args:
            folder_path (Path): The path of the folder to use to find the files.
            problem_id (str): The uid of the problem to load.

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
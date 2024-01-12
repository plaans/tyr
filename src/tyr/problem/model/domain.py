from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from unified_planning.io import PDDLReader
from unified_planning.shortcuts import AbstractProblem

from tyr.patterns import Abstract, AbstractSingletonMeta, Singleton

if TYPE_CHECKING:
    from tyr.problem.model.problem import Problem
    from tyr.problem.model.variant import AbstractVariant


class AbstractDomain(Abstract, Singleton, metaclass=AbstractSingletonMeta):
    """
    Represents the base class for all domains.

    For each supported variant, the class must implements the method
    ``` python
    def build_VARIANT_problem_VERSION(self, problem_id: str) -> Optional[up.AbstractProblem]
    ```
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = self.__class__.__name__[:-6].lower()
        self._variants: Dict[str, "AbstractVariant"] = {}

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the domain.
        """
        return self._name

    @property
    def variants(self) -> Dict[str, "AbstractVariant"]:
        """
        Returns:
            Dict[str, AbstractVariant]: The variants of the domain, indexed by name.
        """
        return self._variants

    def get_problem(
        self,
        variant_name: str,
        problem_id: str,
    ) -> Optional["Problem"]:
        """Builds the problem with the given id in the requested variant.

        Args:
            variant_name (str): The name of the variant responsible to build the problem.
            problem_id (str): The id of the problem to build.

        Returns:
            Optional[Problem]: The generated problem or `None` if the problem doesn't exist.
        """
        if variant_name not in self.variants:
            import tyr.problem  # pylint: disable = import-outside-toplevel, cyclic-import

            variant_class_name = f"{variant_name.title()}Variant"
            variant_class = getattr(tyr.problem, variant_class_name, None)
            if variant_class is None:
                print(f"[WARN] Cannot find class for variant {variant_name}")
                return None

            problem_factory_prefix = f"build_{variant_name}_problem"
            problem_factories = [
                getattr(self, v)
                for v in dir(self)
                if v.startswith(problem_factory_prefix)
            ]
            if len(problem_factories) == 0:
                print(f"[WARN] Cannot find problem builders for variant {variant_name}")
                return None

            self.variants[variant_name] = variant_class(self, problem_factories)

        return self.variants[variant_name].get_problem(problem_id)

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

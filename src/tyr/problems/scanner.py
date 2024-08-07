from importlib import import_module
from pkgutil import walk_packages
from typing import List

from tyr.problems.model.domain import AbstractDomain


def get_all_domains() -> List[AbstractDomain]:
    """
    Returns:
        List[AbstractDomain]: All domains defined in `tyr.problems.domains` module.
    """
    # pylint: disable=import-outside-toplevel, cyclic-import
    import tyr.problems.domains as problem_module

    domains = []

    for _, name, _ in walk_packages(problem_module.__path__):
        module = import_module(f"{problem_module.__name__}.{name}")
        for obj_name in dir(module):
            if obj_name.endswith("Domain") and obj_name not in [
                "AbstractDomain",
                "FolderAbstractDomain",
            ]:
                obj = getattr(module, obj_name)
                if issubclass(obj, AbstractDomain):
                    domains.append(obj())

    return list(set(domains))  # Remove duplicates, note that domains are singleton


__all__ = ["get_all_domains"]

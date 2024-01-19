from importlib import import_module
from pkgutil import walk_packages

from unified_planning.environment import get_environment

from tyr.planners.model.pddl_planner import TyrPDDLPlanner


def register_all_planners():
    """Registers all planners defined in `tyr.planners` into unified planning factory."""
    import tyr.planners as planners_module  # pylint: disable=import-outside-toplevel, cyclic-import

    env = get_environment()
    env.factory.add_engine(
        "aries", "libs.aries.planning.unified.plugin.up_aries", "Aries"
    )

    for _, name, _ in walk_packages(planners_module.__path__):
        module = import_module(f"{planners_module.__name__}.{name}")
        for obj_name in dir(module):
            if obj_name.endswith("Planner") and obj_name not in [
                "Planner",
                "TyrPDDLPlanner",
            ]:
                obj = getattr(module, obj_name)
                if issubclass(obj, TyrPDDLPlanner):
                    env.factory.add_engine(obj().name, module.__name__, obj.__name__)

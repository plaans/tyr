from pathlib import Path
from typing import Dict, Optional

from unified_planning.io import PDDLReader
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.model.scheduling import SchedulingProblem
from unified_planning.model.types import _IntType
from unified_planning.shortcuts import (
    DurativeAction,
    EffectKind,
    EndTiming,
    Not,
    Problem,
    StartTiming,
    LE,
    GE,
)

from tyr.problems.model.instance import ProblemInstance


def get_goals(problem: Problem) -> list:
    """
    Returns:
        list: A flat representation of all goals of the given problem.
    """
    base_goals = problem.goals[:]
    goals = []
    while len(base_goals) > 0:
        goal = base_goals.pop()
        if goal.is_and():
            base_goals.extend(goal.args)
        else:
            goals.append(goal)
    return goals


def reduce_version(problem: ProblemInstance, version: str, number: int) -> Problem:
    """Reduces the number of goals of the given problem.

    Args:
        problem (ProblemInstance): The problem to reduce.
        version (str): The version of the problem to reduce.
        number (int): The number of goals to keep.

    Returns:
        Problem: The reduces problem version.
    """
    base = problem.versions[version].value
    if base is None:
        return None

    result = base.clone()
    goals_subset = get_goals(result)[:number]

    result.clear_goals()
    for goal in goals_subset:
        result.add_goal(goal)

    return result


def goals_to_tasks(
    base_pb: Problem,
    hier_dom_file: Path,
    mapping: Dict[str, str],
    freedom: Optional[Dict[str, str]] = None,
) -> HierarchicalProblem:
    """Converts the goals of the given problem into a hierarchical task network.

    Args:
        base_pb (Problem): The problem to convert.
        hier_dom_file (Path): The file describing the equivalent hierarchical domain.
        mapping (Dict[str, str]): A map from goals name to tasks name.
        freedom (Optional[Dict[str, str]], optional): A type -> task map of freedom.
            Default to None. A task will be created in the task network for every object of type.

    Raises:
        ValueError: When the given file describes a non hierarchical domain.

    Returns:
        HierarchicalProblem: The generated hierarchical problem.
    """

    # Create the hierarchical domain.
    hier_pb = PDDLReader(environment=base_pb.environment).parse_problem(hier_dom_file)
    if not isinstance(hier_pb, HierarchicalProblem):
        raise ValueError(f"{hier_dom_file} does not defined a hierarchical problem")

    # Get the fluents and the tasks from their names.
    trans = {k: hier_pb.get_task(v) for k, v in mapping.items()}

    # Add all objects.
    hier_pb.add_objects(base_pb.all_objects)

    # Initialize all state variables.
    for sv, val in base_pb.explicit_initial_values.items():
        hier_pb.set_initial_value(hier_pb.fluent(sv.fluent().name)(*sv.args), val)

    # Convert each goal into its corresponding task.
    for goal in get_goals(base_pb):
        task = trans[goal.fluent().name]
        hier_pb.task_network.add_subtask(task, *goal.args)

    # Add all metrics.
    for m in base_pb.quality_metrics:
        hier_pb.add_quality_metric(m)

    # Add freedom tasks.
    if freedom:
        for tpe, task_name in freedom.items():
            for obj in hier_pb.objects(hier_pb.user_type(tpe)):
                hier_pb.task_network.add_subtask(hier_pb.get_task(task_name), obj)

    return hier_pb


# pylint: disable = too-many-locals
def scheduling_to_actions(schd_pb: SchedulingProblem) -> Problem:
    """Converts the scheduling problem to a PDDL problem."""

    # Create problem with same name
    pddl_pb = Problem(schd_pb.name)

    # Copy the fluents
    for fluent in schd_pb.fluents:
        pddl_pb.add_fluent(fluent, default_initial_value=schd_pb.initial_value(fluent))
        # Force the integer fluents to be within their bounds at the end
        if isinstance(fluent.type, _IntType):
            if (lb := fluent.type.lower_bound) is not None:
                pddl_pb.add_goal(GE(fluent, lb))
            if (ub := fluent.type.upper_bound) is not None:
                pddl_pb.add_goal(LE(fluent, ub))

    for activity in schd_pb.activities:
        # Convert each activity to a durative action
        action = DurativeAction(activity.name)
        action.set_duration_constraint(activity.duration)

        # Copy each condition
        for interval, conditions in activity.conditions.items():
            for condition in conditions:
                action.add_condition(interval, condition)

        # Copy each effect
        for timing, effects in activity.effects.items():
            for effect in effects:
                if effect.kind == EffectKind.INCREASE:
                    meth = action.add_increase_effect
                elif effect.kind == EffectKind.DECREASE:
                    meth = action.add_decrease_effect
                elif effect.kind == EffectKind.ASSIGN:
                    meth = action.add_effect
                else:
                    raise ValueError(f"Unknown effect kind: {effect.kind}")

                meth(
                    timing,
                    effect.fluent,
                    effect.value,
                    effect.condition,
                    effect.forall,
                )

                # Create a condition to check the new value of the fluent is within its bounds
                if effect.is_increase() or effect.is_decrease():
                    if not isinstance(effect.fluent.type, _IntType):
                        raise ValueError(
                            "Only integer fluents are supported for increases."
                        )
                    if effect.is_increase():
                        val = effect.fluent + effect.value
                    else:
                        val = effect.fluent - effect.value
                    if (lb := effect.fluent.type.lower_bound) is not None:
                        action.add_condition(timing, GE(val, lb))
                    if (ub := effect.fluent.type.upper_bound) is not None:
                        action.add_condition(timing, LE(val, ub))

        # Add a fluent to force the presence of the action (all activities must be present)
        fluent = pddl_pb.add_fluent(f"{action.name}_pres", default_initial_value=False)
        action.add_condition(StartTiming(), Not(fluent))
        action.add_effect(EndTiming(), fluent, True)
        pddl_pb.add_goal(fluent)

        # Save the generated action
        pddl_pb.add_action(action)

    # Add constraints between the actions
    for constraint in schd_pb.base_constraints:
        # Only support `<=` constraints
        assert constraint.is_le()  # nosec: B101

        # Get left and right arguments
        # Suppose the format `end(t_0_0)` for the left and `start(t_0_0)` for the right
        lhs, rhs = tuple(map(str, constraint.args))
        lhs_moment, lhs_action_name = lhs[:-1].split("(")
        rhs_moment, rhs_action_name = rhs[:-1].split("(")
        assert lhs_moment == "end"  # nosec: B101
        assert rhs_moment == "start"  # nosec: B101

        # Get the fluent representing the precence of `lhs` and add it in the conditions of `rhs`
        fluent = pddl_pb.fluent(f"{lhs_action_name}_pres")
        pddl_pb.action(rhs_action_name).add_condition(StartTiming(), fluent)

    # Add problem metrics
    for metric in schd_pb.quality_metrics:
        pddl_pb.add_quality_metric(metric)

    # Return the generated problem
    return pddl_pb


__all__ = [
    "get_goals",
    "reduce_version",
    "goals_to_tasks",
    "scheduling_to_actions",
]

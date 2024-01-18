from pathlib import Path
from typing import Dict

from unified_planning.io import PDDLReader
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.model.scheduling import SchedulingProblem
from unified_planning.shortcuts import (
    DurativeAction,
    EffectKind,
    EndTiming,
    Not,
    Problem,
    StartTiming,
)


def goals_to_tasks(
    base_pb: Problem,
    hier_dom_file: Path,
    mapping: Dict[str, str],
) -> HierarchicalProblem:
    """Converts the goals of the given problem into a hierarchical task network.

    Args:
        base_pb (Problem): The problem to convert.
        hier_dom_file (Path): The file describing the equivalent hierarchical domain.
        mapping (Dict[str, str]): A map from goals name to tasks name.

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
    trans = {hier_pb.fluent(k): hier_pb.get_task(v) for k, v in mapping.items()}

    # Add all objects.
    hier_pb.add_objects(base_pb.all_objects)

    # Initialize all state variables.
    for sv, val in base_pb.explicit_initial_values.items():
        hier_pb.set_initial_value(hier_pb.fluent(sv.fluent().name)(*sv.args), val)

    # Get a flat representation of all goals.
    base_goals = base_pb.goals[:]
    goals = []
    while len(base_goals) > 0:
        goal = base_goals.pop()
        if goal.is_and():
            base_goals.extend(goal.args)
        else:
            goals.append(goal)

    # Convert each goal into its corresponding task.
    for goal in goals:
        task = trans[goal.fluent()]
        hier_pb.task_network.add_subtask(task, *goal.args)

    # Add all metrics.
    for m in base_pb.quality_metrics:
        hier_pb.add_quality_metric(m)

    return hier_pb


# pylint: disable = too-many-locals
def scheduling_to_actions(schd_pb: SchedulingProblem) -> Problem:
    """Converts the scheduling problem to a PDDL problem."""

    # Create problem with same name
    pddl_pb = Problem(schd_pb.name)

    # Copy the fluents
    for fluent in schd_pb.fluents:
        pddl_pb.add_fluent(fluent, default_initial_value=schd_pb.initial_value(fluent))

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

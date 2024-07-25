from collections import OrderedDict
from pathlib import Path
from typing import Dict, Optional, Union

from unified_planning.io import PDDLReader
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.model.scheduling import SchedulingProblem
from unified_planning.model.types import _IntType
from unified_planning.shortcuts import (
    GE,
    LE,
    LT,
    DurationInterval,
    DurativeAction,
    EffectKind,
    EndTiming,
    Equals,
    Fluent,
    FNode,
    InstantaneousAction,
    Minus,
    Not,
    Parameter,
    Plus,
    Problem,
    StartTiming,
    UserType,
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


def reduce_problem(problem: Problem, number: int) -> Problem:
    """Reduces the number of goals of the given problem.

    Args:
        problem (Problem): The problem to reduce.
        number (int): The number of goals to keep.

    Returns:
        Problem: The reduces problem version.
    """
    result = problem.clone()
    goals_subset = get_goals(result)[:number]

    result.clear_goals()
    for goal in goals_subset:
        result.add_goal(goal)

    return result


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
    return reduce_problem(base, number)


def remove_user_typing(problem: Problem) -> Problem:
    # pylint: disable = too-many-locals, too-many-branches, too-many-statements
    """Remove all user typing from the given problem.

    Args:
        problem (Problem): The problem to remove user typing from.

    Returns:
        Problem: The problem without user typing.
    """

    def convert_fnode(fn: FNode):
        # pylint: disable = too-many-return-statements
        if fn.is_bool_constant() or fn.is_int_constant() or fn.is_real_constant():
            return fn
        if fn.is_fluent_exp():
            nf = fluent_map[fn.fluent()]
            na = [convert_fnode(a) for a in fn.args]
            return nf(*na)
        if fn.is_object_exp():
            return new_pb.object(fn.object().name)
        if fn.is_parameter_exp():
            return Parameter(fn.parameter().name, obj_tpe, env)
        if fn.is_not():
            return Not(convert_fnode(fn.args[0]))
        if fn.is_equals():
            return Equals(convert_fnode(fn.args[0]), convert_fnode(fn.args[1]))
        if fn.is_le():
            return LE(convert_fnode(fn.args[0]), convert_fnode(fn.args[1]))
        if fn.is_lt():
            return LT(convert_fnode(fn.args[0]), convert_fnode(fn.args[1]))
        if fn.is_plus():
            return Plus(*[convert_fnode(a) for a in fn.args])
        if fn.is_minus():
            assert len(fn.args) == 2  # nosec: B101
            return Minus(convert_fnode(fn.args[0]), convert_fnode(fn.args[1]))
        raise NotImplementedError(f"Unsupported fluent node: {fn}")

    env = problem.environment
    tm = env.type_manager
    new_pb = Problem(problem.name, env)

    obj_tpe = UserType("tyr_object")
    types_hierarchy: Dict[str, str] = {}
    types_fluents: Dict[str, Fluent] = {}

    # Create the hierarchy of types and create the corresponding fluents
    for parent, children in problem.user_types_hierarchy.items():
        for child in children:
            types_hierarchy[child.name] = parent.name if parent else obj_tpe.name
            types_fluents[child.name] = new_pb.add_fluent(
                Fluent(f"is_{child.name}", tm.BoolType(), None, env, o=obj_tpe)
            )

    # Add all objects and initialize their type fluents
    for obj in problem.all_objects:
        new_obj = new_pb.add_object(obj.name, obj_tpe)
        tpe = obj.type.name
        while tpe != obj_tpe.name:
            new_pb.set_initial_value(types_fluents[tpe](new_obj), True)
            tpe = types_hierarchy[tpe]

    # Copy all fluents with adapted signature
    fluent_map: Dict[Fluent, Fluent] = {}
    for fluent in problem.fluents:
        new_sign = [Parameter(param.name, obj_tpe, env) for param in fluent.signature]
        nf = new_pb.add_fluent(Fluent(fluent.name, fluent.type, new_sign, env))
        fluent_map[fluent] = nf

    # Copy all initial values
    for f, v in problem.initial_values.items():
        new_pb.set_initial_value(convert_fnode(f), v)

    # Copy all timed effects
    for t, el in problem.timed_effects.items():
        for e in el:
            new_pb.add_timed_effect(
                t,
                convert_fnode(e.fluent),
                convert_fnode(e.value),
                e.condition,
                e.forall,
            )

    # Copy all actions with adapted parameters
    for action in problem.actions:
        # pylint: disable = protected-access
        new_params = OrderedDict(((p.name, obj_tpe) for p in action.parameters))
        if isinstance(action, InstantaneousAction):
            new_action: Union[
                InstantaneousAction, DurativeAction
            ] = InstantaneousAction(action.name, new_params, env)
            for op, np in zip(action.parameters, new_action.parameters):
                new_action.add_precondition(types_fluents[op.type.name](np))
            for p in action.preconditions:
                new_action.add_precondition(convert_fnode(p))
            for e in action.effects:
                fluent = convert_fnode(e.fluent)
                if e.is_assignment():
                    new_action.add_effect(
                        fluent, convert_fnode(e.value), e.condition, e.forall
                    )
                elif e.is_increase():
                    new_action.add_increase_effect(
                        fluent, convert_fnode(e.value), e.condition, e.forall
                    )
                elif e.is_decrease():
                    new_action.add_decrease_effect(
                        fluent, convert_fnode(e.value), e.condition, e.forall
                    )
                else:
                    raise NotImplementedError(f"Unsupported effect kind: {e.kind}")
            if action.simulated_effect is not None:
                raise NotImplementedError("Simulated effects are not supported")
        elif isinstance(action, DurativeAction):
            new_action = DurativeAction(action.name, new_params, env)
            for op, np in zip(action.parameters, new_action.parameters):
                new_action.add_condition(StartTiming(), types_fluents[op.type.name](np))
            for i, cl in action.conditions.items():
                for c in cl:
                    new_action.add_condition(i, convert_fnode(c))
            for t, el in action.effects.items():
                for e in el:
                    fluent = convert_fnode(e.fluent)
                    if e.is_assignment():
                        new_action.add_effect(
                            t, fluent, convert_fnode(e.value), e.condition, e.forall
                        )
                    elif e.is_increase():
                        new_action.add_increase_effect(
                            t, fluent, convert_fnode(e.value), e.condition, e.forall
                        )
                    elif e.is_decrease():
                        new_action.add_decrease_effect(
                            t, fluent, convert_fnode(e.value), e.condition, e.forall
                        )
                    else:
                        raise NotImplementedError(f"Unsupported effect kind: {e.kind}")
            for t, _se in action.simulated_effects.items():
                raise NotImplementedError("Simulated effects are not supported")
            new_duration = DurationInterval(
                convert_fnode(action.duration.lower),
                convert_fnode(action.duration.upper),
                action.duration.is_left_open(),
                action.duration.is_right_open(),
            )
            new_action.set_duration_constraint(new_duration)
        else:
            raise NotImplementedError(f"Unsupported action type: {action}")
        new_pb.add_action(new_action)

    # Copy all goals
    for g in problem.goals:
        new_pb.add_goal(convert_fnode(g))

    # Copy all timed goals
    for i, gl in problem.timed_goals.items():
        for g in gl:
            new_pb.add_timed_goal(i, convert_fnode(g))

    # Copy all trajectory constraints
    for t in problem.trajectory_constraints:
        raise NotImplementedError("Trajectory constraints are not supported")

    # Copy all quality metrics
    for m in problem.quality_metrics:
        new_pb.add_quality_metric(m)

    return new_pb


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


# pylint: disable = too-many-locals, too-many-branches
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

                # Create a condition to check the fluent is within its bounds before each effect.
                # Additional check is made in the goal to ensure it is within bounds at the end.
                if effect.is_increase() or effect.is_decrease():
                    if not isinstance(effect.fluent.type, _IntType):
                        raise ValueError(
                            "Only integer fluents are supported for increases."
                        )
                    if (lb := effect.fluent.type.lower_bound) is not None:
                        action.add_condition(timing, GE(effect.fluent, lb))
                    if (ub := effect.fluent.type.upper_bound) is not None:
                        action.add_condition(timing, LE(effect.fluent, ub))

        # Add a fluent to force the presence of the action (all activities must be present)
        fluent = pddl_pb.add_fluent(f"{action.name}_pres", default_initial_value=False)
        action.add_condition(StartTiming(), Not(fluent))
        action.add_effect(EndTiming(), fluent, True)
        pddl_pb.add_goal(fluent)

        # Save the generated action
        pddl_pb.add_action(action)

    # Add constraints between the actions
    for constraint, _act in schd_pb.all_constraints():
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

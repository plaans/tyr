from pathlib import Path
from typing import Dict

from unified_planning.io import PDDLReader
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.shortcuts import Problem


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
    base_goals = base_pb.goals
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

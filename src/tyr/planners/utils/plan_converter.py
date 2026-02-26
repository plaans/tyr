"""Plan conversion utilities for database storage compatibility."""

from typing import Optional

from unified_planning.model import AbstractProblem
from unified_planning.plans import PartialOrderPlan, Plan, PlanKind


def normalize_plan_for_storage(
    plan: Plan,
    problem: Optional[AbstractProblem] = None,
) -> Plan:
    """
    Convert PartialOrderPlans to SequentialPlans for database storage compatibility.

    This ensures that plans stored in the database can be properly consumed by
    warm start methods that expect sequential or temporal plan formats.

    Args:
        plan: The plan to normalize
        problem: The problem instance (required for PartialOrderPlan conversion)

    Returns:
        A normalized plan suitable for database storage and warm start methods

    Raises:
        ValueError: If PartialOrderPlan conversion is attempted without problem instance
    """
    if isinstance(plan, PartialOrderPlan):
        if problem is None:
            raise ValueError(
                "Problem instance is required to convert PartialOrderPlan to SequentialPlan"
            )
        # Convert to sequential plan using topological sort
        return plan.convert_to(PlanKind.SEQUENTIAL_PLAN, problem)

    # Keep other plan types unchanged (SequentialPlan, TimeTriggeredPlan, etc.)
    return plan

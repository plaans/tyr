import inspect
from pathlib import Path
from typing import Any, Callable, List, Optional

from unified_planning.engines.results import LogMessage, PlanGenerationResultStatus
from unified_planning.shortcuts import Problem

from tyr.planners.model.pddl_planner import TyrPDDLPlanner


class ApptainerPlanner(TyrPDDLPlanner):
    """A planner of the IPC stored into a apptainer file."""

    def __init__(self, needs_requirements=True, rewrite_bool_assignments=False) -> None:
        super().__init__(needs_requirements, rewrite_bool_assignments)
        self._plan_found: Optional[bool] = None

    def _get_apptainer_file_name(self) -> str:
        raise NotImplementedError

    def _get_cmd(
        self,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
    ) -> List[str]:
        base = "apptainer run"
        home = Path(domain_filename).parent.as_posix()
        planner_file = inspect.getfile(self.__class__)
        sif = (Path(planner_file).parent / self._get_apptainer_file_name()).as_posix()
        cmd = f"{base} -H {home} -C {sif} {domain_filename} {problem_filename} {plan_filename}"
        return cmd.split()

    def _get_anytime_cmd(
        self,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
    ) -> List[str]:
        return self._get_cmd(domain_filename, problem_filename, plan_filename)

    def _plan_from_str(self, problem: Problem, plan_str: str, get_item_named: Callable):
        lines = plan_str.split("\n")
        plan: List[str] = []
        parsing = False
        for line in lines:
            if line.strip() == "":
                continue
            if line.startswith(self._starting_plan_str()):
                parsing = True
                continue
            if not parsing:
                continue
            if line.startswith(self._ending_plan_str()):
                break
            plan.append(self._parse_plan_line(line))

        if plan:
            self._plan_found = True
        return super()._plan_from_str(problem, "\n".join(plan), get_item_named)

    def _starting_plan_str(self) -> str:
        return "==>"

    def _ending_plan_str(self) -> str:
        return "root"

    def _parse_plan_line(self, plan_line: str) -> str:
        return "(" + " ".join(plan_line.split()[1:]) + ")"

    def _result_status(
        self,
        problem: Problem,
        plan: Optional[Any],
        retval: int,
        log_messages: Optional[List[LogMessage]] = None,
    ) -> PlanGenerationResultStatus:
        if plan is not None and self._plan_found is True:
            return PlanGenerationResultStatus.SOLVED_SATISFICING
        if retval == 0:
            return PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY
        return PlanGenerationResultStatus.INTERNAL_ERROR


__all__ = ["ApptainerPlanner"]

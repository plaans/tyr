import re
import resource
from typing import IO, Callable, Dict, Iterator, Optional

import unified_planning as up
from unified_planning import engines
from unified_planning.engines import mixins, LogMessage, LogLevel
from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)
from unified_planning.shortcuts import AbstractProblem, OneshotPlanner, ProblemKind

from tyr.planners.database import Database
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.planners.aries.planning.unified.plugin.up_aries import Aries
from tyr.planners.scanner import get_all_planners
from tyr.problems.scanner import get_all_domains


class AriesWarmUpPlanner(
    engines.engine.Engine,
    mixins.OneshotPlannerMixin,
    mixins.AnytimePlannerMixin,
):
    """A version of Aries with a warm up plan."""

    _params: Dict[str, str] = {}

    def __init__(self, **kwargs):
        self._params = {k: str(v) for k, v in kwargs.items()}
        super().__init__(**kwargs)

    @property
    def name(self):
        base_name = self.__class__.__name__[:-7]
        return re.sub(r"([A-Z])", r"-\1", base_name).lower().lstrip("-")

    @staticmethod
    def supported_kind() -> ProblemKind:
        return Aries.supported_kind()

    @staticmethod
    def supports(problem_kind) -> bool:
        return Aries.supports(problem_kind)

    def _load_from_db(self, problem: AbstractProblem, timeout: Optional[float] = None):
        # TODO: Be generic for the planner to load
        db = Database()
        optic = [p for p in get_all_planners() if p.name == "aries"].pop()
        domain_name = problem.name.split(":")[0]
        domain = [d for d in get_all_domains() if d.name == domain_name].pop()
        problem_id = int(problem.name.split(":")[1])
        problem_instance = domain.get_problem(problem_id)
        if problem_instance is None:
            raise ValueError(f"Problem {problem.name} not found")
        memout = resource.getrlimit(resource.RLIMIT_AS)[0]
        timeout = int(timeout or 24 * 60 * 60)  # 24 hours by default
        solve_config = SolveConfig(
            jobs=1,
            memout=memout,
            timeout=timeout,
            timeout_offset=0,
            db_only=False,
            no_db_load=False,
            no_db_save=False,
            unify_epsilons=False,
        )

        return db.load_planner_result(
            optic,
            problem_instance,
            solve_config,
            RunningMode.ONESHOT,
        )

    def _solve(
        self,
        problem: AbstractProblem,
        heuristic: Optional[
            Callable[["up.model.state.ROState"], Optional[float]]
        ] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> PlanGenerationResult:
        warm_up_result = self._load_from_db(problem, timeout)
        if warm_up_result is None:
            return PlanGenerationResult(
                PlanGenerationResultStatus.INTERNAL_ERROR,
                plan=None,
                engine_name=self.name,
                log_messages=[LogMessage(LogLevel.ERROR, "Warm up result not found")],
            )

        warm_up_plan = warm_up_result.plan
        if warm_up_plan is None or len(warm_up_plan.splitlines()) <= 1:
            return PlanGenerationResult(
                status=warm_up_result.status,
                plan=warm_up_plan,
                engine_name=self.name,
                log_messages=warm_up_result.log_messages,
                metrics=warm_up_result.metrics,
            )

        params = self._params.copy()
        params["warm_up_plan"] = str(warm_up_plan)
        with OneshotPlanner(name="aries", params=params) as planner:
            return planner.solve(
                problem,
                timeout=timeout - warm_up_result.computation_time,
                output_stream=output_stream,
            )

    def _get_solutions(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> Iterator[PlanGenerationResult]:
        # TODO: Implement the anytime planner
        raise NotImplementedError("_get_solutions method not implemented")

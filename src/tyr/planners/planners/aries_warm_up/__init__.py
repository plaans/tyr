from fractions import Fraction
import os
import re
import resource
from typing import IO, Callable, Dict, Iterator, Optional, Tuple

import unified_planning as up
from unified_planning import engines
from unified_planning.engines import mixins, LogMessage, LogLevel
from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)
from unified_planning.io import PDDLReader
from unified_planning.model.action import DurativeAction, InstantaneousAction
from unified_planning.plans import Plan, PlanKind, SequentialPlan, TimeTriggeredPlan
from unified_planning.shortcuts import (
    AbstractProblem,
    AnytimePlanner,
    EffectKind,
    EndTiming,
    OneshotPlanner,
    ProblemKind,
    StartTiming,
)

from tyr.planners.database import Database
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.result import PlannerResult
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
    optimality_metric_required = False

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

    def _load_from_db(
        self, problem: AbstractProblem, timeout: Optional[float] = None
    ) -> Optional[PlannerResult]:
        db = Database()
        planner_name = os.environ["TYR_WARM_UP_PLANNER"]
        planner = [p for p in get_all_planners() if p.name == planner_name].pop()
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
            planner,
            problem_instance,
            solve_config,
            RunningMode.ONESHOT,
        )

    def _convert_plan_line_to_upf_format(self, line: str) -> str:
        action = (
            line.strip()
            .replace(",", "")
            .replace("(", " ")
            .replace(")", "")
            .replace(": ", ": (")
            .replace(" [", ") [")
        )
        if "(" not in action:
            if ")" in action:
                raise ValueError(f"Invalid action: {action}")
            # Instantaneous action
            return f"({action})"
        return action

    def _convert_plan_to_temporal(self, plan: Plan) -> TimeTriggeredPlan:
        if plan.kind == PlanKind.SEQUENTIAL_PLAN:
            return self._convert_sequential_plan_to_temporal(plan)
        if plan.kind == PlanKind.TIME_TRIGGERED_PLAN:
            return self._convert_time_triggerred_plan_to_temporal(plan)
        raise ValueError(f"Unknown plan kind: {plan.kind}")

    def _convert_sequential_plan_to_temporal(
        self, plan: SequentialPlan
    ) -> TimeTriggeredPlan:
        return self._convert_time_triggerred_plan_to_temporal(
            TimeTriggeredPlan(
                [(Fraction(i, 10), a, 0) for i, a in enumerate(plan.actions)]
            )
        )

    def _convert_time_triggerred_plan_to_temporal(
        self, plan: TimeTriggeredPlan
    ) -> TimeTriggeredPlan:
        actions = []
        for s, a, d in plan.timed_actions:
            action = a.action
            if isinstance(action, InstantaneousAction):
                da = DurativeAction(
                    action.name,
                    _env=action.environment,
                    **{p.name: p.type for p in action.parameters},
                )
                da.set_fixed_duration(0)
                for c in action.preconditions:
                    da.add_condition(StartTiming(), c)
                for e in action.effects:
                    if e.kind == EffectKind.INCREASE:
                        meth = da.add_increase_effect
                    elif e.kind == EffectKind.DECREASE:
                        meth = da.add_decrease_effect
                    elif e.kind == EffectKind.ASSIGN:
                        meth = da.add_effect
                    else:
                        raise ValueError(f"Unknown effect kind: {e.kind}")
                    meth(EndTiming(), e.fluent, e.value, e.condition, e.forall)
                a._action = da  # pylint: disable=protected-access
                d = 0
            actions.append((s, a, d or 0))
        return TimeTriggeredPlan(actions)

    def _set_time_scale(self, problem: AbstractProblem, plan: Plan, time_scale: int):
        if problem.epsilon is None:
            problem.epsilon = Fraction(1, time_scale)

        return (
            self._convert_plan_to_temporal(problem.normalize_plan(plan))
            .convert_to(PlanKind.STN_PLAN, problem)
            .convert_to(PlanKind.TIME_TRIGGERED_PLAN, problem)
        )

    def _load_plan_from_str_with_time_scale(
        self,
        problem: AbstractProblem,
        plan: str,
        time_scale: int,
    ):
        reader = PDDLReader(problem.environment)
        plan = "\n".join(
            [
                self._convert_plan_line_to_upf_format(line)
                for line in plan.splitlines()[1:]  # Skip the first line
            ]
        )
        plan = reader.parse_plan_string(problem, plan)
        return self._set_time_scale(problem, plan, time_scale)

    def _setup_timeout_and_params(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult]:
        warm_up_result = self._load_from_db(problem, timeout)
        if warm_up_result is None:
            # No warm up result found, stop here with an error.
            return (
                None,
                {},
                PlanGenerationResult(
                    PlanGenerationResultStatus.INTERNAL_ERROR,
                    plan=None,
                    engine_name=self.name,
                    log_messages=[
                        LogMessage(LogLevel.ERROR, "Warm up result not found")
                    ],
                ),
            )
        if timeout is None:
            remaining_time = None
        elif warm_up_result.computation_time is None:
            remaining_time = timeout
        else:
            remaining_time = timeout - warm_up_result.computation_time
        warm_up_result.planner = self

        if warm_up_result.plan is None or len(warm_up_result.plan.splitlines()) <= 1:
            warm_up_result.plan = None
        if warm_up_result.plan is not None:
            warm_up_result.plan = self._load_plan_from_str_with_time_scale(
                problem, warm_up_result.plan, 10
            )

        if remaining_time is not None and remaining_time <= 0:
            # No time left for aries, stop here with the original result.
            return None, {}, warm_up_result.to_upf()

        # Solve the problem with the warm up plan and the remaining time.
        params = self._params.copy()
        if warm_up_result.plan is not None:
            params["warm_up_plan"] = str(warm_up_result.plan)
        return remaining_time, params, warm_up_result

    def _solve(
        self,
        problem: AbstractProblem,
        heuristic: Optional[
            Callable[["up.model.state.ROState"], Optional[float]]
        ] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> PlanGenerationResult:
        remaining_time, params, warm_up_result = self._setup_timeout_and_params(
            problem, timeout
        )
        if remaining_time is None:
            return warm_up_result
        with OneshotPlanner(name="aries") as planner:
            result = planner.solve(
                problem,
                heuristic=heuristic,
                timeout=remaining_time,
                output_stream=output_stream,
                **params,
            )
        if result is None or result.plan is None:
            return warm_up_result
        return result

    def _get_solutions(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> Iterator[PlanGenerationResult]:
        remaining_time, params, warm_up_result = self._setup_timeout_and_params(
            problem, timeout
        )
        if remaining_time is None:
            yield warm_up_result
            return
        with AnytimePlanner(name="aries") as planner:
            results = list(
                planner.get_solutions(  # pylint: disable=no-member
                    problem,
                    timeout=remaining_time,
                    output_stream=output_stream,
                    **params,
                )
            )
        if results is None or len(results) == 0:
            yield warm_up_result
            return
        for result in results:
            if result is None or result.plan is None:
                yield warm_up_result
                return
            yield result

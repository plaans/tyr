"""
Aries Warm-Up Planner

This module implements a warm-up strategy for the Aries planner that pre-loads solutions
from a database to provide a starting point for optimization.

Environment Variables:
- TYR_DEBUG_WARM_UP: Enable detailed debug logging (true/1/yes)
- TYR_WARM_UP_PLANNER: Planner name to use for warm-up solutions
- TYR_WARM_UP_STRATEGY: Strategy to use (first_solution, timeout_fallback, optimized_warmstart)
- TYR_WARM_UP_TIME_RATIO: Time ratio for fallback strategies (default: 0.5)

Debug Mode:
When TYR_DEBUG_WARM_UP is enabled, the planner will log detailed information about:
- Parameter conversion and initialization
- Database queries and results
- Plan conversion steps and intermediate results
- Strategy selection and execution
- Error details with full tracebacks
"""

from enum import Enum
from fractions import Fraction
from math import ceil
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
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.planners.planners.aries.planning.unified.plugin.up_aries import Aries
from tyr.planners.scanner import get_all_planners
from tyr.problems.scanner import get_all_domains


class WarmUpStrategy(Enum):
    """Strategies for warm-up planning."""

    FIRST_SOLUTION = "first_solution"
    TIMEOUT_FALLBACK = "timeout_fallback"
    OPTIMIZED_WARMSTART = "optimized_warmstart"


class AriesWarmUpPlanner(
    engines.engine.Engine,
    mixins.OneshotPlannerMixin,
    mixins.AnytimePlannerMixin,
):
    """A version of Aries with a warm up plan."""

    _params: Dict[str, str] = {}
    optimality_metric_required = False

    # =============================== Core Methods =============================== #

    def __init__(self, **kwargs):
        try:
            # Debug logging for parameter conversion
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: AriesWarmUpPlanner.__init__ called with kwargs: {kwargs}")
                for k, v in kwargs.items():
                    print(f"DEBUG: Converting parameter '{k}' (type {type(k).__name__}) = {v} (type {type(v).__name__})")
                    
            self._params = {}
            for k, v in kwargs.items():
                if not isinstance(k, str):
                    error_msg = f"Parameter key must be string, got {type(k).__name__}: {k}"
                    print(f"ERROR: {error_msg}")
                    raise TypeError(error_msg)
                self._params[k] = str(v)
                
            if debug_mode:
                print(f"DEBUG: Successfully converted parameters: {self._params}")
                
        except Exception as e:
            print(f"ERROR: Exception in AriesWarmUpPlanner.__init__ during parameter conversion:")
            print(f"  kwargs: {kwargs}")
            print(f"  Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
            
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

    # ============================ Main Solver Methods =========================== #

    def _solve(
        self,
        problem: AbstractProblem,
        heuristic: Optional[
            Callable[["up.model.state.ROState"], Optional[float]]
        ] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> PlanGenerationResult:
        (
            remaining_time,
            params,
            warm_up_result,
            warm_up_time,
        ) = self._setup_timeout_and_params(problem, timeout)
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
        if (result is None or 
            result.plan is None or 
            result.status == PlanGenerationResultStatus.INTERNAL_ERROR):
            return warm_up_result

        # Add warm-up time to the Aries result's computation time
        if warm_up_time is not None and result.metrics is not None:
            if "engine_internal_time" in result.metrics:
                aries_time = float(result.metrics["engine_internal_time"])
                total_time = aries_time + warm_up_time
                result.metrics["engine_internal_time"] = str(total_time)
        elif warm_up_time is not None:
            if result.metrics is None:
                result.metrics = {}
            result.metrics["engine_internal_time"] = str(warm_up_time)

        return result

    def _get_solutions(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> Iterator[PlanGenerationResult]:
        (
            remaining_time,
            params,
            warm_up_result,
            warm_up_time,
        ) = self._setup_timeout_and_params(problem, timeout)
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
            if (result is None or 
                result.plan is None or 
                result.status == PlanGenerationResultStatus.INTERNAL_ERROR):
                yield warm_up_result
                return

            # Add warm-up time to the Aries result's computation time
            if warm_up_time is not None and result.metrics is not None:
                if "engine_internal_time" in result.metrics:
                    aries_time = float(result.metrics["engine_internal_time"])
                    total_time = aries_time + warm_up_time
                    result.metrics["engine_internal_time"] = str(total_time)
            elif warm_up_time is not None:
                if result.metrics is None:
                    result.metrics = {}
                result.metrics["engine_internal_time"] = str(warm_up_time)

            yield result

    # ====================== Database and Conversion Helpers ===================== #

    def _load_from_db(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        running_mode: RunningMode = RunningMode.ONESHOT,
        max_computation_time: Optional[float] = None,
    ) -> Optional[PlannerResult]:
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _load_from_db called:")
                print(f"  problem.name: {problem.name}")
                print(f"  timeout: {timeout}")
                print(f"  running_mode: {running_mode}")
                print(f"  max_computation_time: {max_computation_time}")

            db = Database()
            planner_name = os.environ["TYR_WARM_UP_PLANNER"]
            
            if debug_mode:
                print(f"DEBUG: Loading planner '{planner_name}'")
            
            planner = [p for p in get_all_planners() if p.name == planner_name].pop()
            domain_name = problem.name.split(":")[0]
            domain = [d for d in get_all_domains() if d.name == domain_name].pop()
            problem_id = int(problem.name.split(":")[1])
            
            if debug_mode:
                print(f"DEBUG: Parsed problem - domain: '{domain_name}', id: {problem_id}")
                
            problem_instance = domain.get_problem(problem_id)
            if problem_instance is None:
                error_msg = f"Problem {problem.name} not found in domain {domain_name}"
                print(f"ERROR: {error_msg}")
                raise ValueError(error_msg)
                
            memout = resource.getrlimit(resource.RLIMIT_AS)[0]
            timeout = int(timeout or 24 * 60 * 60)  # 24 hours by default
            
            if debug_mode:
                print(f"DEBUG: Creating SolveConfig - memout: {memout}, timeout: {timeout}")
                
            solve_config = SolveConfig(
                jobs=1,
                memout=memout,
                timeout=ceil(max_computation_time or timeout),
                timeout_offset=0,
                db_only=False,
                no_db_load=False,
                no_db_save=False,
                unify_epsilons=False,
            )

            if debug_mode:
                print(f"DEBUG: Loading warm-up planner result from database")
                
            result = db.load_warm_up_planner_result(
                planner,
                problem_instance,
                solve_config,
                running_mode,
                keep_unsupported=True,
                not_run_by_default=True,
            )
            
            if debug_mode:
                if result:
                    print(f"DEBUG: Database result found - status: {result.status}, plan length: {len(result.plan or '')}")
                else:
                    print(f"DEBUG: No database result found")
                    
            return result
            
        except Exception as e:
            print(f"ERROR: Exception in _load_from_db:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  planner_name: {os.environ.get('TYR_WARM_UP_PLANNER', 'NOT_SET')}")
            print(f"  Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _convert_db_result_to_upf(
        self,
        warm_up_result: PlannerResult,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult]:
        """Convert database PlannerResult to the format expected by strategy methods."""
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _convert_db_result_to_upf called:")
                print(f"  problem.name: {problem.name}")
                print(f"  timeout: {timeout}")
                print(f"  warm_up_result.status: {warm_up_result.status}")
                print(f"  warm_up_result.computation_time: {warm_up_result.computation_time}")
                print(f"  warm_up_result.plan length: {len(warm_up_result.plan or '')}")
                
            if timeout is None:
                remaining_time = None
            elif warm_up_result.computation_time is None:
                remaining_time = timeout
            else:
                remaining_time = timeout - warm_up_result.computation_time

            if debug_mode:
                print(f"DEBUG: Calculated remaining_time: {remaining_time}")

            warm_up_result.planner = self
            warm_up_result.from_database = False

            if warm_up_result.plan is None or len(warm_up_result.plan.splitlines()) <= 1:
                warm_up_result.plan = None
                warm_up_result.status = PlannerResultStatus.TIMEOUT
                if debug_mode:
                    print(f"DEBUG: Plan is empty or too short, setting to None")
            else:
                if debug_mode:
                    print(f"DEBUG: Converting plan with time scale 10")
                    print(f"DEBUG: Original plan preview: {warm_up_result.plan[:200]}...")
                
                try:
                    warm_up_result.plan = self._load_plan_from_str_with_time_scale(
                        problem, warm_up_result.plan, 10
                    )
                    if debug_mode:
                        print(f"DEBUG: Plan conversion successful")
                except Exception as plan_error:
                    print(f"ERROR: Failed to convert plan with time scale:")
                    print(f"  Problem: {problem.name}")
                    print(f"  Plan preview: {warm_up_result.plan[:200]}...")
                    print(f"  Error: {type(plan_error).__name__}: {plan_error}")
                    import traceback
                    traceback.print_exc()
                    raise

            if remaining_time is not None and remaining_time <= 0:
                if debug_mode:
                    print(f"DEBUG: No remaining time, returning early")
                return None, {}, warm_up_result.to_upf()

            params = self._params.copy()
            if warm_up_result.plan is not None:
                try:
                    plan = str(warm_up_result.plan)
                    if debug_mode:
                        print(f"DEBUG: Creating warm_start_plan parameter from plan")
                    params["warm_start_plan"] = self._plan_from_str(problem, plan)
                except Exception as plan_param_error:
                    print(f"ERROR: Failed to create warm_start_plan parameter:")
                    print(f"  Problem: {problem.name}")
                    print(f"  Error: {type(plan_param_error).__name__}: {plan_param_error}")
                    import traceback
                    traceback.print_exc()
                    raise
                    
            if debug_mode:
                print(f"DEBUG: _convert_db_result_to_upf completed successfully")
                print(f"DEBUG: Final params keys: {list(params.keys())}")
                
            return remaining_time, params, warm_up_result.to_upf()
            
        except Exception as e:
            print(f"ERROR: Exception in _convert_db_result_to_upf:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

    # ========================= Warm-Up Strategy Methods ========================= #

    def _setup_timeout_and_params(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult, Optional[float]]:
        """Main strategy dispatcher - selects and executes appropriate warm-up strategy."""
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _setup_timeout_and_params called:")
                print(f"  problem.name: {problem.name}")
                print(f"  timeout: {timeout}")
                
            strategy_name = os.environ.get(
                "TYR_WARM_UP_STRATEGY",
                WarmUpStrategy.FIRST_SOLUTION.name,
            )
            strategy = WarmUpStrategy(strategy_name.lower())
            time_ratio = float(os.environ.get("TYR_WARM_UP_TIME_RATIO", "0.5"))

            if debug_mode:
                print(f"DEBUG: Using strategy '{strategy.value}' with time_ratio {time_ratio}")
                print(f"DEBUG: Environment variables:")
                print(f"  TYR_WARM_UP_PLANNER: {os.environ.get('TYR_WARM_UP_PLANNER', 'NOT_SET')}")
                print(f"  TYR_WARM_UP_STRATEGY: {strategy_name}")
                print(f"  TYR_WARM_UP_TIME_RATIO: {os.environ.get('TYR_WARM_UP_TIME_RATIO', '0.5')}")

            if strategy == WarmUpStrategy.FIRST_SOLUTION:
                if debug_mode:
                    print(f"DEBUG: Executing FIRST_SOLUTION strategy")
                return self._first_solution_strategy(problem, timeout)
            if strategy == WarmUpStrategy.TIMEOUT_FALLBACK:
                if debug_mode:
                    print(f"DEBUG: Executing TIMEOUT_FALLBACK strategy")
                return self._timeout_fallback_strategy(problem, timeout, time_ratio)
            if strategy == WarmUpStrategy.OPTIMIZED_WARMSTART:
                if debug_mode:
                    print(f"DEBUG: Executing OPTIMIZED_WARMSTART strategy")
                return self._optimized_warmstart_strategy(problem, timeout, time_ratio)
                
            error_msg = (
                f"Unknown warm-up strategy: {strategy_name}. "
                f"Supported strategies: {[s.value for s in WarmUpStrategy]}"
            )
            print(f"ERROR: {error_msg}")
            raise ValueError(error_msg)
            
        except Exception as e:
            print(f"ERROR: Exception in _setup_timeout_and_params:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  strategy_name: {os.environ.get('TYR_WARM_UP_STRATEGY', 'NOT_SET')}")
            print(f"  Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _first_solution_strategy(
        self, problem: AbstractProblem, timeout: Optional[float] = None
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult, Optional[float]]:
        """
        First Solution Strategy:
        Load first solution from database with computation_time < timeout,
        then use remaining time for Aries optimization.
        """
        warm_up_result = self._load_from_db(
            problem,
            timeout,
            RunningMode.ONESHOT,
            max_computation_time=timeout,
        )

        if warm_up_result is None or warm_up_result.plan is None:
            # No solution found within time constraint
            return (
                None,
                {},
                PlanGenerationResult(
                    PlanGenerationResultStatus.TIMEOUT,
                    plan=None,
                    engine_name=self.name,
                    log_messages=[
                        LogMessage(
                            LogLevel.INFO,
                            "No warm-up solution found in first solution strategy",
                        )
                    ],
                ),
                None,
            )

        remaining_time, params, upf_result = self._convert_db_result_to_upf(
            warm_up_result, problem, timeout
        )
        warm_up_time = (
            warm_up_result.computation_time
            if warm_up_result.computation_time is not None
            else 0.0
        )
        return remaining_time, params, upf_result, warm_up_time

    def _timeout_fallback_strategy(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        time_ratio: float = 0.5,
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult, Optional[float]]:
        """
        Timeout with Fallback Strategy:
        Check database for solutions with computation_time < timeout*ratio.
        If solution found, warm-start Aries with remaining time.
        If no solution, run Aries from scratch with remaining time.
        """
        if timeout is None:
            # Without timeout, just try to get a solution quickly
            return self._first_solution_strategy(problem, None)

        warm_up_timeout = timeout * time_ratio
        remaining_time = timeout * (1 - time_ratio)

        warm_up_result = self._load_from_db(
            problem,
            timeout,
            RunningMode.ONESHOT,
            max_computation_time=warm_up_timeout,
        )

        if warm_up_result is not None and warm_up_result.plan is not None:
            # Solution found - warm-start Aries with remaining time
            remaining_time, params, upf_result = self._convert_db_result_to_upf(
                warm_up_result, problem, timeout
            )
            return remaining_time, params, upf_result, warm_up_timeout

        # No solution found - run Aries from scratch with remaining time
        return (
            remaining_time,
            self._params.copy(),
            PlanGenerationResult(
                PlanGenerationResultStatus.TIMEOUT,
                plan=None,
                engine_name=self.name,
                log_messages=[
                    LogMessage(
                        LogLevel.INFO,
                        f"No warm-up solution found within {warm_up_timeout}s",
                    )
                ],
            ),
            warm_up_timeout,
        )

    def _optimized_warmstart_strategy(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        time_ratio: float = 0.5,
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult, Optional[float]]:
        """
        Optimized Warm-Start Strategy:
        Load best solution from ANYTIME database results
        with computation_time < timeout*ratio,
        then warm-start Aries with remaining time.
        """
        if timeout is None:
            # Without timeout, try to get any ANYTIME solution
            warm_up_timeout = None
            remaining_time = None
        else:
            warm_up_timeout = timeout * time_ratio
            remaining_time = timeout * (1 - time_ratio)

        warm_up_result = self._load_from_db(
            problem,
            timeout,
            RunningMode.ANYTIME,
            max_computation_time=warm_up_timeout,
        )

        if warm_up_result is not None and warm_up_result.plan is not None:
            # Best solution found - warm-start Aries with remaining time
            remaining_time, params, upf_result = self._convert_db_result_to_upf(
                warm_up_result, problem, timeout
            )
            return remaining_time, params, upf_result, warm_up_timeout

        # No solution found - run Aries from scratch with remaining time
        return (
            remaining_time,
            self._params.copy(),
            PlanGenerationResult(
                PlanGenerationResultStatus.TIMEOUT,
                plan=None,
                engine_name=self.name,
                log_messages=[
                    LogMessage(
                        LogLevel.INFO,
                        f"No optimized warm-up solution found within {warm_up_timeout}s",
                    )
                ],
            ),
            warm_up_timeout,
        )

    # ========================== Plan Conversion Methods ========================= #

    def _convert_plan_line_to_upf_format(self, line: str) -> str:
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _convert_plan_line_to_upf_format input: '{line}'")
                
            action = (
                line.strip()
                .replace(",", "")
                .replace("(", " ")
                .replace(")", "")
                .replace(": ", ": (")
                .replace(" [", ") [")
            )
            
            if debug_mode:
                print(f"DEBUG: After replacements: '{action}'")
                
            if "(" not in action:
                if ")" in action:
                    error_msg = f"Invalid action: {action}"
                    print(f"ERROR: {error_msg}")
                    raise ValueError(error_msg)
                # Instantaneous action
                result = f"({action})"
                if debug_mode:
                    print(f"DEBUG: Instantaneous action result: '{result}'")
                return result
                
            if debug_mode:
                print(f"DEBUG: Action result: '{action}'")
            return action
            
        except Exception as e:
            print(f"ERROR: Exception in _convert_plan_line_to_upf_format:")
            print(f"  Input line: '{line}'")
            print(f"  Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

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
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _set_time_scale called:")
                print(f"  problem.name: {problem.name}")
                print(f"  time_scale: {time_scale}")
                print(f"  problem.epsilon: {problem.epsilon}")
                print(f"  plan.kind: {plan.kind}")
                
            if problem.epsilon is None:
                problem.epsilon = Fraction(1, time_scale)
                if debug_mode:
                    print(f"DEBUG: Set problem.epsilon to {problem.epsilon}")

            if debug_mode:
                print(f"DEBUG: Normalizing plan")
            try:
                normalized_plan = problem.normalize_plan(plan)
                if debug_mode:
                    print(f"DEBUG: Plan normalized successfully")
            except Exception as normalize_error:
                print(f"ERROR: Failed to normalize plan:")
                print(f"  Problem: {problem.name}")
                print(f"  Plan kind: {plan.kind}")
                print(f"  Error: {type(normalize_error).__name__}: {normalize_error}")
                import traceback
                traceback.print_exc()
                raise

            if debug_mode:
                print(f"DEBUG: Converting plan to temporal")
            try:
                temporal_plan = self._convert_plan_to_temporal(normalized_plan)
                if debug_mode:
                    print(f"DEBUG: Plan converted to temporal successfully")
            except Exception as temporal_error:
                print(f"ERROR: Failed to convert plan to temporal:")
                print(f"  Problem: {problem.name}")
                print(f"  Error: {type(temporal_error).__name__}: {temporal_error}")
                import traceback
                traceback.print_exc()
                raise

            if debug_mode:
                print(f"DEBUG: Converting to STN_PLAN")
            try:
                stn_plan = temporal_plan.convert_to(PlanKind.STN_PLAN, problem)
                if debug_mode:
                    print(f"DEBUG: Plan converted to STN successfully")
            except Exception as stn_error:
                print(f"ERROR: Failed to convert plan to STN:")
                print(f"  Problem: {problem.name}")
                print(f"  Error: {type(stn_error).__name__}: {stn_error}")
                import traceback
                traceback.print_exc()
                raise
                
            if debug_mode:
                print(f"DEBUG: Converting to TIME_TRIGGERED_PLAN")
            try:
                result = stn_plan.convert_to(PlanKind.TIME_TRIGGERED_PLAN, problem)
                if debug_mode:
                    print(f"DEBUG: _set_time_scale completed successfully")
                return result
            except Exception as time_triggered_error:
                print(f"ERROR: Failed to convert plan to TIME_TRIGGERED:")
                print(f"  Problem: {problem.name}")
                print(f"  Error: {type(time_triggered_error).__name__}: {time_triggered_error}")
                import traceback
                traceback.print_exc()
                raise
                
        except Exception as e:
            print(f"ERROR: Exception in _set_time_scale:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  time_scale: {time_scale}")
            print(f"  Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _load_plan_from_str_with_time_scale(
        self,
        problem: AbstractProblem,
        plan: str,
        time_scale: int,
    ):
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _load_plan_from_str_with_time_scale called:")
                print(f"  problem.name: {problem.name}")
                print(f"  plan length: {len(plan)}")
                print(f"  time_scale: {time_scale}")
                print(f"  plan preview: {plan[:200]}...")
                
            reader = PDDLReader(problem.environment)
            
            if debug_mode:
                print(f"DEBUG: Converting plan lines to UPF format")
                
            try:
                plan_lines = plan.splitlines()[1:]  # Skip the first line
                if debug_mode:
                    print(f"DEBUG: Processing {len(plan_lines)} plan lines")
                    
                converted_lines = []
                for i, line in enumerate(plan_lines):
                    try:
                        converted_line = self._convert_plan_line_to_upf_format(line)
                        converted_lines.append(converted_line)
                        if debug_mode and i < 3:  # Log first few lines
                            print(f"DEBUG: Line {i}: '{line}' -> '{converted_line}'")
                    except Exception as line_error:
                        print(f"ERROR: Failed to convert plan line {i}: '{line}'")
                        print(f"  Error: {type(line_error).__name__}: {line_error}")
                        raise
                        
                plan = "\n".join(converted_lines)
                if debug_mode:
                    print(f"DEBUG: Converted plan preview: {plan[:200]}...")
                    
            except Exception as convert_error:
                print(f"ERROR: Failed during plan line conversion:")
                print(f"  Problem: {problem.name}")
                print(f"  Error: {type(convert_error).__name__}: {convert_error}")
                import traceback
                traceback.print_exc()
                raise
            
            if debug_mode:
                print(f"DEBUG: Parsing plan string with PDDLReader")
                
            try:
                plan = reader.parse_plan_string(problem, plan)
                if debug_mode:
                    print(f"DEBUG: Plan parsing successful")
            except Exception as parse_error:
                print(f"ERROR: Failed to parse plan string:")
                print(f"  Problem: {problem.name}")
                print(f"  Plan content: {plan}")
                print(f"  Error: {type(parse_error).__name__}: {parse_error}")
                import traceback
                traceback.print_exc()
                raise
            
            if debug_mode:
                print(f"DEBUG: Setting time scale")
                
            try:
                result = self._set_time_scale(problem, plan, time_scale)
                if debug_mode:
                    print(f"DEBUG: _load_plan_from_str_with_time_scale completed successfully")
                return result
            except Exception as scale_error:
                print(f"ERROR: Failed to set time scale:")
                print(f"  Problem: {problem.name}")
                print(f"  time_scale: {time_scale}")
                print(f"  Error: {type(scale_error).__name__}: {scale_error}")
                import traceback
                traceback.print_exc()
                raise
                
        except Exception as e:
            print(f"ERROR: Exception in _load_plan_from_str_with_time_scale:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  time_scale: {time_scale}")
            print(f"  plan length: {len(plan) if plan else 0}")
            print(f"  Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _plan_line_to_upf_format(self, line: str) -> str:
        line = line.strip().replace(",", " ").replace("(", " ").replace(": ", ": (")
        if ")" not in line:
            line = line.replace(" [", ") [")
        return line

    def _plan_from_str(self, problem: AbstractProblem, plan: str) -> Plan:
        reader = PDDLReader(problem.environment)
        plan = "\n".join(map(self._plan_line_to_upf_format, plan.splitlines()[1:]))
        return reader.parse_plan_string(problem, plan)

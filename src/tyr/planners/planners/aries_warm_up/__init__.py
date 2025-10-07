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

        debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")

        try:
            with AnytimePlanner(name="aries") as planner:
                # Yield results iteratively as they arrive instead of collecting them all
                has_yielded = False
                for result in planner.get_solutions(  # pylint: disable=no-member
                    problem,
                    timeout=remaining_time,
                    output_stream=output_stream,
                    **params,
                ):
                    if result is None or result.plan is None or result.status == PlanGenerationResultStatus.INTERNAL_ERROR:
                        if debug_mode:
                            print(f"DEBUG: Skipping invalid result from Aries")
                        continue

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
                    has_yielded = True

                # If no valid results were yielded, yield the warm-up result
                if not has_yielded:
                    if debug_mode:
                        print(f"DEBUG: No valid results from Aries, yielding warm-up result")
                    yield warm_up_result

        except Exception as e:
            # Handle gRPC errors and other exceptions gracefully
            error_type = type(e).__name__
            if debug_mode:
                print(f"WARNING: Exception in _get_solutions (anytime mode): {error_type}: {e}")
                import traceback
                traceback.print_exc()

            # For gRPC errors, yield the warm-up result as fallback
            if "grpc" in error_type.lower() or "MultiThreadedRendezvous" in error_type:
                if debug_mode:
                    print(f"DEBUG: gRPC connection error, yielding warm-up result as fallback")
                yield warm_up_result
            else:
                # For other errors, re-raise
                raise

    # ====================== Base Planner Execution ===================== #

    def _save_warmup_results(self, warm_up_results: list[PlannerResult], problem: AbstractProblem):
        """Save warm-up results to the database with the warm-up planner name.

        Args:
            warm_up_results: List of results from the base planner (can include intermediate results)
            problem: The problem being solved
        """
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: Saving {len(warm_up_results)} warm-up result(s) to database")
                print(f"  Planner name: {self.name}")
                print(f"  Problem: {problem.name}")

            # Update the planner reference to this warm-up planner and save each result
            from dataclasses import replace
            db = Database()

            for idx, warm_up_result in enumerate(warm_up_results):
                if debug_mode:
                    print(f"DEBUG: Saving result {idx + 1}/{len(warm_up_results)} - Status: {warm_up_result.status}")

                warmup_result_to_save = replace(warm_up_result, planner=self, from_database=False)
                db.save_planner_result(warmup_result_to_save)

            if debug_mode:
                print(f"DEBUG: Successfully saved all {len(warm_up_results)} warm-up result(s)")

        except Exception as e:
            print(f"WARNING: Failed to save warm-up results to database:")
            print(f"  Error: {type(e).__name__}: {e}")
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                import traceback
                traceback.print_exc()
            # Continue even if saving fails

    def _run_base_planner(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        running_mode: RunningMode = RunningMode.ONESHOT,
    ) -> Optional[Tuple[list[PlannerResult], PlannerResult, float]]:
        """Run the base planner and return all results.

        Args:
            problem: The problem to solve
            timeout: Maximum time allowed for the base planner
            running_mode: Whether to run in oneshot or anytime mode

        Returns:
            Tuple of (all_results, last_result, actual_computation_time) or None if failed
        """
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _run_base_planner called:")
                print(f"  problem.name: {problem.name}")
                print(f"  timeout: {timeout}")
                print(f"  running_mode: {running_mode}")

            # Get the base planner
            planner_name = os.environ["TYR_WARM_UP_PLANNER"]

            if debug_mode:
                print(f"DEBUG: Getting planner '{planner_name}'")

            planner = [p for p in get_all_planners() if p.name == planner_name].pop()

            # Parse problem name to get domain and problem instance
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

            # Create solve config
            memout = resource.getrlimit(resource.RLIMIT_AS)[0]
            base_timeout = int(timeout or 24 * 60 * 60)  # 24 hours by default

            if debug_mode:
                print(f"DEBUG: Creating SolveConfig - memout: {memout}, timeout: {base_timeout}")

            solve_config = SolveConfig(
                jobs=1,
                memout=memout,
                timeout=base_timeout,
                timeout_offset=0,
                db_only=False,
                no_db_load=True,  # Don't load from DB, always run fresh
                no_db_save=True,  # Don't save with base planner name - we'll save with warm-up name
                unify_epsilons=False,
            )

            if debug_mode:
                print(f"DEBUG: Running base planner '{planner_name}' in {running_mode} mode")

            # Run the base planner and collect ALL results
            import time
            start_time = time.time()
            results = list(planner.solve(problem_instance, solve_config, running_mode))
            actual_time = time.time() - start_time

            if not results:
                if debug_mode:
                    print(f"DEBUG: No results from base planner")
                return None

            # Get the last result (best for anytime, only for oneshot)
            last_result = results[-1]

            if debug_mode:
                print(f"DEBUG: Base planner returned {len(results)} result(s)")
                print(f"DEBUG: Last result - status: {last_result.status}, actual_time: {actual_time}")
                if last_result.plan:
                    print(f"DEBUG: Base planner found a plan")

            # Save ALL results to database with warm-up planner name
            self._save_warmup_results(results, problem)

            return results, last_result, actual_time

        except Exception as e:
            print(f"WARNING: Exception in _run_base_planner, returning None:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  planner_name: {os.environ.get('TYR_WARM_UP_PLANNER', 'NOT_SET')}")
            print(f"  Error: {type(e).__name__}: {e}")
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                import traceback
                traceback.print_exc()
            # Return None so Aries will run without warm-start
            return None

    def _convert_planner_result_to_upf(
        self,
        warm_up_result: PlannerResult,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult]:
        """Convert PlannerResult to the format expected by strategy methods."""
        try:
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                print(f"DEBUG: _convert_planner_result_to_upf called:")
                print(f"  problem.name: {problem.name}")
                print(f"  timeout: {timeout}")
                print(f"  warm_up_result.status: {warm_up_result.status}")
                print(f"  warm_up_result.computation_time: {warm_up_result.computation_time}")
                plan_repr = str(warm_up_result.plan) if warm_up_result.plan else ""
                print(f"  warm_up_result.plan length: {len(plan_repr)}")

            if timeout is None:
                remaining_time = None
            elif warm_up_result.computation_time is None:
                remaining_time = timeout
            else:
                remaining_time = timeout - warm_up_result.computation_time

            if debug_mode:
                print(f"DEBUG: Calculated remaining_time: {remaining_time}")

            # Check if we have a valid plan
            has_plan = warm_up_result.plan is not None
            if has_plan and isinstance(warm_up_result.plan, str):
                # Plan from database is a string - check if it's valid
                has_plan = len(warm_up_result.plan.splitlines()) > 1

            if not has_plan:
                if debug_mode:
                    print(f"DEBUG: No valid plan from base planner")
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
                                "No solution from base planner",
                            )
                        ],
                    ),
                    None,
                )

            # Handle plan conversion based on type
            plan_for_warmstart = None
            if isinstance(warm_up_result.plan, Plan):
                # Plan object from fresh planner run - use directly
                if debug_mode:
                    print(f"DEBUG: Using Plan object directly for warm-start")
                try:
                    plan_for_warmstart = self._set_time_scale(problem, warm_up_result.plan, 10)
                    if debug_mode:
                        print(f"DEBUG: Plan time scale conversion successful")
                except Exception as plan_error:
                    print(f"WARNING: Failed to convert plan time scale, will ignore warm-start:")
                    print(f"  Problem: {problem.name}")
                    print(f"  Error: {type(plan_error).__name__}: {plan_error}")
                    if debug_mode:
                        import traceback
                        traceback.print_exc()
            elif isinstance(warm_up_result.plan, str):
                # Plan string from database - parse it
                if debug_mode:
                    print(f"DEBUG: Converting plan string with time scale 10")
                    print(f"DEBUG: Original plan preview: {warm_up_result.plan[:200]}...")
                try:
                    plan_for_warmstart = self._load_plan_from_str_with_time_scale(
                        problem, warm_up_result.plan, 10
                    )
                    if debug_mode:
                        print(f"DEBUG: Plan string conversion successful")
                except Exception as plan_error:
                    print(f"WARNING: Failed to convert plan string, will ignore warm-start:")
                    print(f"  Problem: {problem.name}")
                    print(f"  Plan preview: {warm_up_result.plan[:200]}...")
                    print(f"  Error: {type(plan_error).__name__}: {plan_error}")
                    if debug_mode:
                        import traceback
                        traceback.print_exc()

            if remaining_time is not None and remaining_time <= 0:
                if debug_mode:
                    print(f"DEBUG: No remaining time, returning early")
                return None, {}, warm_up_result.to_upf(), None

            params = self._params.copy()
            if plan_for_warmstart is not None:
                try:
                    plan_str = str(plan_for_warmstart)
                    if debug_mode:
                        print(f"DEBUG: Creating warm_start_plan parameter from plan")
                    params["warm_start_plan"] = self._plan_from_str(problem, plan_str)
                except Exception as plan_param_error:
                    print(f"WARNING: Failed to create warm_start_plan parameter, falling back to normal planning:")
                    print(f"  Problem: {problem.name}")
                    print(f"  Error: {type(plan_param_error).__name__}: {plan_param_error}")
                    if debug_mode:
                        import traceback
                        traceback.print_exc()
                    # Don't add warm_start_plan parameter - let Aries plan from scratch
                    if debug_mode:
                        print(f"DEBUG: Continuing with normal planning without warm-start")

            if debug_mode:
                print(f"DEBUG: _convert_planner_result_to_upf completed successfully")
                print(f"DEBUG: Final params keys: {list(params.keys())}")

            return remaining_time, params, warm_up_result.to_upf(), warm_up_result.computation_time
            
        except Exception as e:
            print(f"WARNING: Exception in _convert_planner_result_to_upf, falling back to normal planning:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  Error: {type(e).__name__}: {e}")
            debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")
            if debug_mode:
                import traceback
                traceback.print_exc()
            # Return fallback result - normal planning with remaining time
            return (
                timeout,
                self._params.copy(),
                PlanGenerationResult(
                    PlanGenerationResultStatus.TIMEOUT,
                    plan=None,
                    engine_name=self.name,
                    log_messages=[
                        LogMessage(
                            LogLevel.INFO,
                            f"Warm-start conversion failed, proceeding with normal planning",
                        )
                    ],
                ),
                None,
            )

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
            print(f"WARNING: Exception in _setup_timeout_and_params, falling back to normal planning:")
            print(f"  problem.name: {getattr(problem, 'name', 'UNKNOWN')}")
            print(f"  strategy_name: {os.environ.get('TYR_WARM_UP_STRATEGY', 'NOT_SET')}")
            print(f"  Error: {type(e).__name__}: {e}")
            if debug_mode:
                import traceback
                traceback.print_exc()
            # Return fallback - normal planning with all available time
            return (
                timeout,
                self._params.copy(),
                PlanGenerationResult(
                    PlanGenerationResultStatus.TIMEOUT,
                    plan=None,
                    engine_name=self.name,
                    log_messages=[
                        LogMessage(
                            LogLevel.INFO,
                            f"Warm-start strategy failed, proceeding with normal planning",
                        )
                    ],
                ),
                None,
            )

    def _first_solution_strategy(
        self, problem: AbstractProblem, timeout: Optional[float] = None
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult, Optional[float]]:
        """
        First Solution Strategy:
        Run base planner in oneshot mode with full timeout,
        then use remaining time for Aries optimization.
        """
        debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")

        # Run base planner in oneshot mode with full timeout
        result = self._run_base_planner(
            problem,
            timeout,
            RunningMode.ONESHOT,
        )

        if result is None:
            # Base planner failed - run Aries from scratch with full timeout
            if debug_mode:
                print(f"DEBUG: Base planner failed, running Aries from scratch")
            return (
                timeout,
                self._params.copy(),
                PlanGenerationResult(
                    PlanGenerationResultStatus.TIMEOUT,
                    plan=None,
                    engine_name=self.name,
                    log_messages=[
                        LogMessage(
                            LogLevel.INFO,
                            "Base planner failed in first solution strategy",
                        )
                    ],
                ),
                None,
            )

        # Unpack all results (already saved by _run_base_planner)
        all_results, warm_up_result, actual_time = result

        # Convert result for Aries warm-start
        remaining_time, params, upf_result, warm_up_time = self._convert_planner_result_to_upf(
            warm_up_result, problem, timeout
        )

        if debug_mode:
            print(f"DEBUG: First solution strategy - {len(all_results)} result(s) saved, warm_up_time: {warm_up_time}, remaining: {remaining_time}")

        return remaining_time, params, upf_result, warm_up_time or actual_time

    def _timeout_fallback_strategy(
        self,
        problem: AbstractProblem,
        timeout: Optional[float] = None,
        time_ratio: float = 0.5,
    ) -> Tuple[Optional[float], Dict[str, str], PlanGenerationResult, Optional[float]]:
        """
        Timeout with Fallback Strategy:
        Run base planner in oneshot mode with timeout*ratio.
        If solution found, warm-start Aries with remaining time.
        If no solution, run Aries from scratch with remaining time.
        """
        debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")

        if timeout is None:
            # Without timeout, just try to get a solution quickly
            return self._first_solution_strategy(problem, None)

        warm_up_timeout = timeout * time_ratio
        remaining_time = timeout * (1 - time_ratio)

        if debug_mode:
            print(f"DEBUG: Fallback strategy - warm_up_timeout: {warm_up_timeout}, remaining: {remaining_time}")

        # Run base planner in oneshot mode with allocated timeout
        result = self._run_base_planner(
            problem,
            warm_up_timeout,
            RunningMode.ONESHOT,
        )

        if result is not None:
            # Unpack all results (already saved by _run_base_planner)
            all_results, warm_up_result, actual_time = result

            # Check if we got a valid plan
            if warm_up_result.plan is not None:
                # Solution found - warm-start Aries with remaining time
                if debug_mode:
                    print(f"DEBUG: Base planner found solution ({len(all_results)} result(s) saved), warm-starting Aries")

                # Recalculate remaining time based on actual execution time
                remaining_time = timeout - actual_time

                remaining_time, params, upf_result, _ = self._convert_planner_result_to_upf(
                    warm_up_result, problem, timeout
                )
                return remaining_time, params, upf_result, actual_time

        # No solution found - run Aries from scratch with remaining time
        if debug_mode:
            print(f"DEBUG: No solution from base planner, running Aries from scratch")

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
        Run base planner in anytime mode with timeout*ratio,
        use best solution to warm-start Aries with remaining time.
        """
        debug_mode = os.environ.get("TYR_DEBUG_WARM_UP", "").lower() in ("true", "1", "yes")

        if timeout is None:
            # Without timeout, try to get any ANYTIME solution
            warm_up_timeout = None
            remaining_time = None
        else:
            warm_up_timeout = timeout * time_ratio
            remaining_time = timeout * (1 - time_ratio)

        if debug_mode:
            print(f"DEBUG: Optimized strategy - warm_up_timeout: {warm_up_timeout}, remaining: {remaining_time}")

        # Run base planner in anytime mode with allocated timeout
        result = self._run_base_planner(
            problem,
            warm_up_timeout,
            RunningMode.ANYTIME,
        )

        if result is not None:
            # Unpack all results (already saved by _run_base_planner)
            all_results, warm_up_result, actual_time = result

            # Check if we got a valid plan
            if warm_up_result.plan is not None:
                # Best solution found - warm-start Aries with remaining time
                if debug_mode:
                    print(f"DEBUG: Base planner found optimized solution ({len(all_results)} result(s) saved), warm-starting Aries")

                # Recalculate remaining time based on actual execution time
                if timeout is not None:
                    remaining_time = timeout - actual_time

                remaining_time, params, upf_result, _ = self._convert_planner_result_to_upf(
                    warm_up_result, problem, timeout
                )
                return remaining_time, params, upf_result, actual_time

        # No solution found - run Aries from scratch with remaining time
        if debug_mode:
            print(f"DEBUG: No optimized solution from base planner, running Aries from scratch")

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

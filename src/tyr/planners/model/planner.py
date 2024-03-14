import os
import resource
import shutil
import signal
import time
import traceback
from io import TextIOWrapper
from pathlib import Path
from typing import Generator, Optional, Tuple

import unified_planning.shortcuts as upf
from unified_planning.engines import PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.environment import get_environment
from unified_planning.shortcuts import AbstractProblem, Engine

from tyr.core.constants import LOGS_DIR
from tyr.planners.database import Database
from tyr.planners.model.config import PlannerConfig, RunningMode, SolveConfig
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems import ProblemInstance


class Planner:
    """Represents a task planner wrapping unified planning library."""

    def __init__(self, config: PlannerConfig) -> None:
        self._config = config
        self._last_upf_result: Optional[PlanGenerationResult] = None

    @property
    def config(self) -> PlannerConfig:
        """
        Returns:
            PlannerConfig: The configuration of the planner.
        """
        return self._config

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the planner.
        """
        return self.config.name

    @property
    def anytime_name(self) -> str:
        """
        Returns:
            str: The name of the planner for anytime resolution.
        """
        if self.config.anytime_name is None:
            return self.name
        return self.config.anytime_name

    @property
    def oneshot_name(self) -> str:
        """
        Returns:
            str: The name of the planner for oneshot resolution.
        """
        if self.config.oneshot_name is None:
            return self.name
        return self.config.oneshot_name

    @property
    def last_upf_result(self) -> Optional[PlanGenerationResult]:
        """
        Returns:
            Optional[PlanGenerationResult]: The last result of the resolution in upf format.
        """
        return self._last_upf_result

    def get_log_file(
        self,
        problem: ProblemInstance,
        file_name: str,
        running_mode: RunningMode,
    ) -> Path:
        """The file where the planner can write its logs for the given problem.

        Args:
            problem (ProblemInstance): The problem concerned by the logs.
            file_name (str): The name of the file to write in.
            running_mode (RunningMode): The mode used for the resolution.

        Returns:
            Path: The path of the log file.
        """
        folder = (
            LOGS_DIR
            / self.name
            / problem.domain.name
            / f"{problem.uid}-{running_mode.name.lower()}"
        )
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{file_name}.log"

    def get_version(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        """Search the version that the planner has to solve for the given problem.

        Args:
            problem (ProblemInstance): The problem to solve.

        Returns:
            Optional[AbstractProblem]: The version to solve. `None` if it is not supported.
        """
        try:
            version_name = self.config.problems[problem.domain.name]
            return problem.versions[version_name].value
        except KeyError:
            return None

    # pylint: disable = too-many-locals, too-many-branches, too-many-statements
    def solve(
        self,
        problem: ProblemInstance,
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> PlannerResult:
        """Tries to solve the given problem with the given configuration.

        Args:
            problem (ProblemInstance): The problem to solve.
            config (SolveConfig): The configuration to use during the resolution.
            running_mode (RunningMode): The mode to use to run the resolution.

        Returns:
            PlannerResult: The result of the resolution.
        """
        # Get the planner based on the running mode.
        if running_mode == RunningMode.ONESHOT:
            builder = upf.OneshotPlanner
            planner_name = self.oneshot_name
        else:
            builder = upf.AnytimePlanner
            planner_name = self.anytime_name

        # Get the version to solve.
        version = self.get_version(problem)
        if version is None:
            # No version found, the problem is not supported.
            return PlannerResult.unsupported(problem, self, config, running_mode)

        # Check the database.
        if config.no_db is False:
            db = Database().load_planner_result(
                planner_name,
                problem,
                config,
                running_mode,
            )
            if db is not None:
                return db
            if config.db_only:
                return PlannerResult.not_run(problem, self, config, running_mode)

        # Limits the virtual memory of the current process.
        resource.setrlimit(resource.RLIMIT_AS, (config.memout, resource.RLIM_INFINITY))

        # Set the environment variables specified in the planner config.
        for env_name, env_value in self.config.env.items():
            os.environ[env_name] = env_value

        # Clear the logs.
        shutil.rmtree(self.get_log_file(problem, "", running_mode).parent, True)

        # Start recording time in case the second `start` is not reached because of an error.
        start = time.time()
        try:
            # Disable credits.
            get_environment().credits_stream = None
            with builder(name=planner_name) as planner:
                # Disable compatibility checking.
                planner.skip_checks = True
                # Get the log file.
                log_path = self.get_log_file(problem, "solve", running_mode)
                with open(log_path, "w", encoding="utf-8") as log_file:
                    try:
                        end = start + config.timeout
                        self._last_upf_result = None
                        # Set the timeout alarm.
                        signal.signal(signal.SIGALRM, self._solve_timed_out)
                        signal.alarm(config.timeout)
                        # Get the solutions.
                        if running_mode == RunningMode.ONESHOT:
                            self._last_upf_result, start, end = self._solve_oneshot(
                                planner,
                                version,
                                config.timeout,
                                log_file,
                            )
                        else:
                            for result, s, e in self._solve_anytime(
                                planner,
                                version,
                                config.timeout,
                                log_file,
                            ):
                                self._last_upf_result = result
                                start, end = s, e
                        # Disable the timeout alarm.
                        signal.alarm(0)
                    except TimeoutError:
                        # The planner timed out.
                        # Kill the process if it is still running.
                        if hasattr(planner, "_process"):
                            try:
                                planner._process.kill()  # pylint: disable=protected-access
                            except OSError:
                                pass  # This can happen if the process is already terminated
                        # Return a timeout result if no result was found.
                        if self.last_upf_result is None:
                            return PlannerResult.timeout(
                                problem,
                                self,
                                config,
                                running_mode,
                            )

            if self.last_upf_result is not None:
                # Save the plan in logs
                plan_path = self.get_log_file(problem, "plan", running_mode)
                with open(plan_path, "w", encoding="utf-8") as log_file:
                    log_file.write(str(self.last_upf_result.plan))

            # Convert the result into inner format and set computation time if not present.
            result = PlannerResult.from_upf(
                problem,
                self.last_upf_result,
                config,
                running_mode,
            )
            if (
                self.last_upf_result is not None
                and self.last_upf_result.plan is not None
                and self.last_upf_result.status == PlanGenerationResultStatus.TIMEOUT
            ):
                # On anytime mode, last result can be timeout even if an intermediate was solved.
                result.status = PlannerResultStatus.SOLVED
            if result.computation_time is None:
                result.computation_time = end - start
            return result

        except Exception:  # pylint: disable=broad-exception-caught
            # An error occured...
            log_path = self.get_log_file(problem, "error", running_mode)
            with open(log_path, "w", encoding="utf-8") as log_file:
                log_file.write(traceback.format_exc())
            computation_time = time.time() - start
            return PlannerResult.error(
                problem,
                self,
                config,
                running_mode,
                computation_time,
                traceback.format_exc(),
            )

    def _solve_anytime(
        self,
        planner: Engine,
        version: AbstractProblem,
        timeout: int,
        log_file: TextIOWrapper,
    ) -> Generator[
        Tuple[PlanGenerationResult, float, float],
        None,
        Tuple[PlanGenerationResult, float, float],
    ]:
        # Record time and try the solve the problem.
        start = time.time()
        final_result = None
        for result in planner.get_solutions(
            version,
            timeout=timeout,
            output_stream=log_file,
        ):
            final_result = result
            yield result, start, time.time()
        return final_result, start, time.time()

    def _solve_oneshot(
        self,
        planner: Engine,
        version: AbstractProblem,
        timeout: int,
        log_file: TextIOWrapper,
    ) -> Tuple[PlanGenerationResult, float, float]:
        # Record time and try the solve the problem.
        start = time.time()
        upf_result = planner.solve(
            version,
            timeout=timeout,
            output_stream=log_file,
        )
        end = time.time()
        return upf_result, start, end

    @staticmethod
    def _solve_timed_out(signum, frame):
        raise TimeoutError("The planner timed out.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Planner):
            return False
        return self.config == other.config

    def __hash__(self) -> int:
        return hash(self.config)

    def __str__(self) -> str:
        return self.name


__all__ = ["Planner"]

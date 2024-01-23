import os
import resource
import shutil
import time
import traceback
from pathlib import Path
from typing import Generator, Optional, Tuple

import unified_planning.shortcuts as upf
from timeout_decorator import timeout
from unified_planning.engines import PlanGenerationResult
from unified_planning.shortcuts import AbstractProblem

from tyr.core.constants import LOGS_DIR
from tyr.planners.model.config import PlannerConfig, RunningMode, SolveConfig
from tyr.planners.model.result import PlannerResult
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

    # pylint: disable = too-many-locals
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
        # Get the version to solve.
        version = self.get_version(problem)
        if version is None:
            # No version found, the problem is not supported.
            return PlannerResult.unsupported(problem, self, running_mode)

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
            # Get the planner and the log file.
            if running_mode == RunningMode.ONESHOT:
                builder = upf.OneshotPlanner
                name = self.oneshot_name
            else:
                builder = upf.AnytimePlanner
                name = self.anytime_name
            with builder(name=name) as planner:
                # Disable compatibility checking
                planner.skip_checks = True
                log_path = self.get_log_file(problem, "solve", running_mode)
                with open(log_path, "w", encoding="utf-8") as log_file:
                    # Create the resolution fonctions with timeout decorator in case that
                    # the planner does not handle it itself.
                    @timeout(
                        config.timeout,
                        use_signals=config.jobs == 1,
                        timeout_exception=TimeoutError,
                    )
                    def resolution_anytime() -> (
                        Generator[
                            Tuple[PlanGenerationResult, float, float],
                            None,
                            Tuple[PlanGenerationResult, float, float],
                        ]
                    ):
                        # Record time and try the solve the problem.
                        start = time.time()
                        result = None
                        # pylint: disable = no-member
                        for result in planner.get_solutions(
                            version,
                            timeout=config.timeout,
                            output_stream=log_file,
                        ):
                            yield result, start, time.time()
                        return result, start, time.time()

                    @timeout(
                        config.timeout,
                        use_signals=config.jobs == 1,
                        timeout_exception=TimeoutError,
                    )
                    def resolution_oneshot() -> (
                        Tuple[PlanGenerationResult, float, float]
                    ):
                        # Record time and try the solve the problem.
                        start = time.time()
                        upf_result = planner.solve(
                            version,
                            timeout=config.timeout,
                            output_stream=log_file,
                        )
                        end = time.time()
                        return upf_result, start, end

                    try:
                        end = start + config.timeout
                        if running_mode == RunningMode.ONESHOT:
                            self._last_upf_result, start, end = resolution_oneshot()
                        else:
                            for result, s, e in resolution_anytime():
                                self._last_upf_result = result
                                start, end = s, e
                    except TimeoutError:
                        # The planner timed out.
                        if self.last_upf_result is None:
                            return PlannerResult.timeout(
                                problem,
                                self,
                                running_mode,
                                config.timeout,
                            )

            # Convert the result into inner format and set computation time if not present.
            result = PlannerResult.from_upf(problem, self.last_upf_result, running_mode)
            if result.computation_time is None:
                result.computation_time = end - start
            if result.computation_time > config.timeout:
                # The timeout has been reached...
                return PlannerResult.timeout(
                    problem,
                    self,
                    running_mode,
                    config.timeout,
                )
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
                running_mode,
                computation_time,
                traceback.format_exc(),
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Planner):
            return False
        return self.config == other.config

    def __hash__(self) -> int:
        return hash(self.config)

import os
import resource
import shutil
import signal
import time
import traceback
from pathlib import Path
from typing import Optional

import unified_planning.shortcuts as upf
from unified_planning.shortcuts import AbstractProblem

from tyr.core.constants import LOGS_DIR
from tyr.planners.model.config import PlannerConfig, SolveConfig
from tyr.planners.model.result import PlannerResult
from tyr.problems import ProblemInstance


def _timeout_handler(signum, frame):
    raise TimeoutError


class Planner:
    """Represents a task planner wrapping unified planning library."""

    def __init__(self, config: PlannerConfig) -> None:
        self._config = config

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

    def get_log_file(self, problem: ProblemInstance, file_name: str) -> Path:
        """The file where the planner can write its logs for the given problem.

        Args:
            problem (ProblemInstance): The problem concerned by the logs.
            file_name (str): The name of the file to write in.

        Returns:
            Path: The path of the log file.
        """
        folder = LOGS_DIR / self.name / problem.domain.name / problem.uid
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

    def solve(self, problem: ProblemInstance, config: SolveConfig) -> PlannerResult:
        """Tries to solve the given problem with the given configuration.

        Args:
            problem (ProblemInstance): The problem to solve.
            config (SolveConfig): The configuration to use during the resolution.

        Returns:
            PlannerResult: The result of the resolution.
        """
        # Get the version to solve.
        version = self.get_version(problem)
        if version is None:
            # No version found, the problem is not supported.
            return PlannerResult.unsupported(problem, self)

        # Limits the virtual memory of the current process.
        resource.setrlimit(resource.RLIMIT_AS, (config.memout, resource.RLIM_INFINITY))

        # Set the environment variables specified in the planner config.
        for env_name, env_value in self.config.env.items():
            os.environ[env_name] = env_value

        # Clear the logs.
        shutil.rmtree(self.get_log_file(problem, "").parent, True)

        # Start recording time in case the second `start` is not reached because of an error.
        start = time.time()
        try:
            # Get the planner and the log file.
            with upf.OneshotPlanner(name=self.name) as planner:
                # Disable compatibility checking
                planner.skip_checks = True
                log_path = self.get_log_file(problem, "solve")
                with open(log_path, "w", encoding="utf-8") as log_file:
                    # Prepare own timeout procedure in case the planner doesn't timeout by itself.
                    signal.signal(signal.SIGALRM, _timeout_handler)
                    signal.alarm(config.timeout)
                    try:
                        # Record time and try the solve the problem.
                        start = time.time()
                        upf_result = planner.solve(
                            version,
                            timeout=config.timeout,
                            output_stream=log_file,
                        )
                        end = time.time()
                    except TimeoutError:
                        # The planner timed out.
                        return PlannerResult.timeout(problem, self, config.timeout)
                    finally:
                        # Disable the timeout alarm.
                        signal.alarm(0)

            # Convert the result into inner format and set computation time if not present.
            result = PlannerResult.from_upf(problem, upf_result)
            if result.computation_time is None:
                result.computation_time = end - start
            if result.computation_time > config.timeout:
                # The timeout has been reached...
                return PlannerResult.timeout(problem, self, config.timeout)
            return result

        except Exception:  # pylint: disable=broad-exception-caught
            # An error occured...
            log_path = self.get_log_file(problem, "error")
            with open(log_path, "w", encoding="utf-8") as log_file:
                log_file.write(traceback.format_exc())
            computation_time = time.time() - start
            return PlannerResult.error(problem, self, computation_time)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Planner):
            return False
        return self.config == other.config

    def __hash__(self) -> int:
        return hash(self.config)

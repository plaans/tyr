import os
import resource
import shutil
import time
import traceback
import warnings
from dataclasses import replace
from io import TextIOWrapper
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from typing import Generator, Optional, Tuple

import unified_planning.shortcuts as upf
from unified_planning.engines import PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.environment import get_environment
from unified_planning.exceptions import UPException
from unified_planning.grpc.proto_writer import ProtobufWriter
from unified_planning.shortcuts import AbstractProblem, Engine

from tyr.core.paths import TyrPaths
from tyr.planners.database import Database
from tyr.planners.model.config import PlannerConfig, RunningMode, SolveConfig
from tyr.planners.model.pddl_writer import TyrPDDLWriter
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems import ProblemInstance

warnings.filterwarnings("ignore", category=UserWarning)


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
        extension: str = "log",
    ) -> Path:
        """The file where the planner can write its logs for the given problem.

        Args:
            problem (ProblemInstance): The problem concerned by the logs.
            file_name (str): The name of the file to write in.
            running_mode (RunningMode): The mode used for the resolution.
            extension (str, optional): The extension of the log file. Defaults to "log".

        Returns:
            Path: The path of the log file, created if it does not exist.
        """
        folder = (
            TyrPaths().logs
            / self.name
            / problem.domain.name
            / f"{problem.uid}-{running_mode.name.lower()}"
        )
        folder.mkdir(parents=True, exist_ok=True)
        file = folder / f"{file_name}.{extension}"
        file.touch()
        return file

    def get_version(
        self, problem: ProblemInstance
    ) -> Tuple[Optional[str], Optional[AbstractProblem]]:
        """Search the version that the planner has to solve for the given problem.

        Args:
            problem (ProblemInstance): The problem to solve.

        Returns:
            Optional[AbstractProblem]: The version to solve and its name.
                `None` for both if it is not supported.
        """
        version_name = self.config.problems.get(problem.domain.name, "base")
        try:
            return version_name, problem.versions[version_name].value
        except KeyError:
            return None, None

    def supports_running_mode(self, running_mode: RunningMode) -> bool:
        """
        Checks if the planner supports the given running mode.

        Args:
            running_mode (RunningMode): The mode to check.

        Returns:
            bool: `True` if the planner supports the mode, `False` otherwise.
        """
        unsupported_name = "unsupported-mode"
        if running_mode == RunningMode.ONESHOT:
            return self.oneshot_name != unsupported_name
        if running_mode == RunningMode.ANYTIME:
            return self.anytime_name != unsupported_name
        raise NotImplementedError(f"Running mode {running_mode} is not supported.")

    def solve(
        self,
        problem: ProblemInstance,
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> Generator[PlannerResult, None, None]:
        """
        Tries to solve the given problem with the given configuration.

        Args:
            problem (ProblemInstance): The problem to solve.
            config (SolveConfig): The configuration to use during the resolution.
            running_mode (RunningMode): The mode to use to run the resolution.

        Returns:
            Generator[PlannerResult, None, None]: The results of the resolution.
        """
        start = time.time()
        try:
            for result in self._solve(problem, config, running_mode):
                if config.no_db_save is False:
                    Database().save_planner_result(result)
                yield result
        except Exception:  # pylint: disable=broad-exception-caught
            # Save the error in logs.
            log_path = self.get_log_file(problem, "error", running_mode)
            with open(log_path, "w", encoding="utf-8") as log_file:
                log_file.write(traceback.format_exc())
            # Return an error or memout result.
            computation_time = time.time() - start
            yield PlannerResult.error(
                problem,
                self,
                config,
                running_mode,
                computation_time,
                traceback.format_exc(),
            )

    def solve_single(
        self,
        problem: ProblemInstance,
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> PlannerResult:
        """
        Tries to solve the given problem with the given configuration.

        Args:
            problem (ProblemInstance): The problem to solve.
            config (SolveConfig): The configuration to use during the resolution.
            running_mode (RunningMode): The mode to use to run the resolution.

        Returns:
            Generator[PlannerResult, None, None]: The last result of the resolution.
        """
        return list(self.solve(problem, config, running_mode)).pop()

    # pylint: disable = too-many-locals, too-many-branches, too-many-statements
    # pylint: disable = too-many-return-statements
    def _solve(
        self,
        problem: ProblemInstance,
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> Generator[PlannerResult, None, None]:
        """Tries to solve the given problem with the given configuration.

        Args:
            problem (ProblemInstance): The problem to solve.
            config (SolveConfig): The configuration to use during the resolution.
            running_mode (RunningMode): The mode to use to run the resolution.

        Returns:
            Generator[PlannerResult, None, None]: The results of the resolution.
        """
        # Check if the planner supports the running mode.
        if not self.supports_running_mode(running_mode):
            yield PlannerResult.unsupported(problem, self, config, running_mode)
            return

        # Get the planner based on the running mode.
        if running_mode == RunningMode.ONESHOT:
            builder = upf.OneshotPlanner
            upf_planner_name = self.oneshot_name
            solve_target = self._solve_oneshot
        elif running_mode == RunningMode.ANYTIME:
            builder = upf.AnytimePlanner
            upf_planner_name = self.anytime_name
            solve_target = self._solve_anytime
        else:
            raise NotImplementedError(f"Running mode {running_mode} is not supported.")

        # Check the database.
        if config.no_db_load is False:
            db = Database().load_planner_result(
                self.name,
                problem,
                config,
                running_mode,
            )
            if db is not None:
                yield db
                return
            if config.db_only:
                yield PlannerResult.not_run(problem, self, config, running_mode)
                return

        # Get the version to solve.
        version_name, version = self.get_version(problem)
        if version_name is None or version is None:
            # No version found, the problem is not supported.
            yield PlannerResult.unsupported(problem, self, config, running_mode)
            return

        # Clear the logs and logs the version to solve.
        shutil.rmtree(self.get_log_file(problem, "", running_mode).parent, True)
        self._log_problem_version(problem, version, running_mode)

        # Limits the virtual memory of the current process.
        resource.setrlimit(resource.RLIMIT_AS, (config.memout, resource.RLIM_INFINITY))

        # Set the environment variables specified in the planner config.
        for env_name, env_value in self.config.env.items():
            os.environ[env_name] = env_value

        # Start recording time in case the second `start` is not reached because of an error.
        start = time.time()
        try:
            # Disable credits.
            get_environment().credits_stream = None
            process: Optional[Process] = None
            with builder(name=upf_planner_name) as planner:
                # Disable compatibility checking.
                planner.skip_checks = True
                # Get the log file.
                log_path = self.get_log_file(problem, "output", running_mode)
                with open(log_path, "w", encoding="utf-8") as log_file:
                    end = start + config.timeout
                    self._last_upf_result = None
                    # Use a multiprocessing queue to get the results from the child process.
                    queue: Queue = Queue()
                    process = Process(
                        target=solve_target,
                        args=(planner, version, config.timeout, log_file, queue),
                    )
                    process.start()
                    start_process = time.time()
                    # Get the results from the queue.
                    while (
                        time.time() - start_process
                        < config.timeout + config.timeout_offset
                    ):
                        if not process.is_alive() and queue.empty():
                            break
                        try:
                            result = queue.get(timeout=0.1)
                            if isinstance(result, Exception):
                                raise result
                            self._last_upf_result, start, end = result
                            if running_mode == RunningMode.ONESHOT:
                                break
                            yield self._handle_upf_result(
                                self.last_upf_result,
                                self.name,
                                problem,
                                version_name,
                                running_mode,
                                config,
                                (start, end),
                            )
                        except Empty:
                            continue
                    # The planner timed out.
                    if process.is_alive():
                        # Kill the process if it is still running.
                        process.terminate()
                        process.join(2)
                        if process.is_alive():
                            process.kill()
                        # Return a timeout result if no result was found.
                        if self.last_upf_result is None:
                            yield PlannerResult.timeout(
                                problem,
                                self,
                                config,
                                running_mode,
                            )
                            return

            yield self._handle_upf_result(
                self.last_upf_result,
                self.name,
                problem,
                version_name,
                running_mode,
                config,
                (start, end),
            )
            return

        except Exception:  # pylint: disable=broad-exception-caught
            # An error occured...
            # Stop the process if it is still running.
            if process is not None and process.is_alive():
                process.terminate()
                process.join(2)
                if process.is_alive():
                    process.kill()
            # Save the error in logs.
            log_path = self.get_log_file(problem, "error", running_mode)
            with open(log_path, "w", encoding="utf-8") as log_file:
                log_file.write(traceback.format_exc())
            # Generate the error result.
            computation_time = time.time() - start
            result = PlannerResult.error(
                problem,
                self,
                config,
                running_mode,
                computation_time,
                traceback.format_exc(),
            )
            # Check if a special status can be found in the logs.
            log_path = self.get_log_file(problem, "output", running_mode)
            if special_status := self._check_special_status_from_logs(log_path):
                result = replace(result, status=special_status)
            yield result
            return

    def _log_problem_version(
        self,
        problem: ProblemInstance,
        version: AbstractProblem,
        running_mode: RunningMode,
    ) -> None:
        # pylint: disable = broad-exception-caught

        # Export the problem in PDDL format.
        try:
            dom_path = self.get_log_file(problem, "domain", running_mode, "pddl")
            prb_path = self.get_log_file(problem, "problem", running_mode, "pddl")
            TyrPDDLWriter(version, needs_requirements=True).write_domain(
                dom_path.as_posix(), all_support=True
            )
            TyrPDDLWriter(version, needs_requirements=True).write_problem(prb_path)
        except UPException as error:
            err_path = self.get_log_file(problem, "pddl_export_error", running_mode)
            err_path.write_text(str(error))

        # Export the problem in UPF binary format.
        try:
            bin_path = self.get_log_file(problem, "problem", running_mode, "binpb")
            bin_path.write_bytes(ProtobufWriter().convert(version).SerializeToString())
        except Exception as error:
            err_path = self.get_log_file(problem, "bin_export_error", running_mode)
            err_path.write_text(str(error))

        # Export the problem in TXT format.
        txt_path = self.get_log_file(problem, "problem", running_mode, "txt")
        txt_path.write_text(str(version))

    def _solve_anytime(  # pylint: disable = too-many-arguments
        self,
        planner: Engine,
        version: AbstractProblem,
        timeout: int,
        log_file: TextIOWrapper,
        queue: Queue,
    ) -> None:
        try:
            # Record time and try the solve the problem.
            start = time.time()
            for result in planner.get_solutions(
                version,
                timeout=timeout,
                output_stream=log_file,
            ):
                if result.status != PlanGenerationResultStatus.TIMEOUT:
                    queue.put((result, start, time.time()))
        except Exception as error:  # pylint: disable=broad-exception-caught
            queue.put(error)

    def _solve_oneshot(  # pylint: disable = too-many-arguments
        self,
        planner: Engine,
        version: AbstractProblem,
        timeout: int,
        log_file: TextIOWrapper,
        queue: Queue,
    ) -> None:
        try:
            # Record time and try the solve the problem.
            start = time.time()
            upf_result = planner.solve(
                version,
                timeout=timeout,
                output_stream=log_file,
            )
            end = time.time()
            queue.put((upf_result, start, end))
        except Exception as error:  # pylint: disable=broad-exception-caught
            queue.put(error)

    # pylint: disable = too-many-arguments
    def _handle_upf_result(
        self,
        upf_result: PlanGenerationResult,
        planner_name: str,
        problem: ProblemInstance,
        version_name: str,
        running_mode: RunningMode,
        config: SolveConfig,
        times: Tuple[float, float],
    ) -> PlannerResult:
        # Convert the result into inner format and set computation time if not present.
        result = PlannerResult.from_upf(
            planner_name,
            problem,
            version_name,
            upf_result,
            config,
            running_mode,
        )
        if result.computation_time is None:
            result.computation_time = times[1] - times[0]

        if upf_result is not None:
            # Save the plan in logs
            plan_path = self.get_log_file(problem, "plan", running_mode)
            with open(plan_path, "w", encoding="utf-8") as log_file:
                log_file.write(str(upf_result.plan))

        if upf_result is not None and upf_result.plan is not None:
            splitted = str(upf_result.plan).strip().split("\n")
            has_plan = len(splitted) > 1
        else:
            has_plan = False
        if (
            has_plan
            and upf_result.status == PlanGenerationResultStatus.TIMEOUT
            and running_mode == RunningMode.ANYTIME
        ):
            # On anytime mode, last result can be timeout even if an intermediate was solved.
            result.status = PlannerResultStatus.SOLVED

        # Check if a special status can be found in the logs if the result is not solved.
        log_path = self.get_log_file(problem, "output", running_mode)
        if (
            status := self._check_special_status_from_logs(log_path)
        ) is not None and result.status != PlannerResultStatus.SOLVED:
            result = replace(result, status=status)
        return result

    # ============================================================================ #
    #                             Special Planner Cases                            #
    # ============================================================================ #

    def _check_special_status_from_logs(
        self, logs: Path
    ) -> Optional[PlannerResultStatus]:
        callback = getattr(self, f"_check_special_status_from_logs_{self.name}", None)
        if callback is None:
            return None

        with open(logs, "r", encoding="utf-8") as log_file:
            for line in log_file:
                if (res := callback(line)) is not None:
                    return res
        return None

    # =================================== Aries ================================== #

    def _check_special_status_from_logs_aries(
        self, line: str
    ) -> Optional[PlannerResultStatus]:
        if line.startswith("memory") and line.endswith("failed\n"):
            return PlannerResultStatus.MEMOUT
        return None

    # ==================================== LPG =================================== #

    def _check_special_status_from_logs_lpg(
        self, line: str
    ) -> Optional[PlannerResultStatus]:
        if line in ["Max time exceeded.\n", "Error: max cpu-time reached\n"]:
            return PlannerResultStatus.TIMEOUT
        return None

    # ============================================================================ #
    #                            Python's Magic Methods                            #
    # ============================================================================ #

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Planner):
            return False
        return self.config == other.config

    def __hash__(self) -> int:
        return hash(self.config)

    def __str__(self) -> str:
        return self.name


__all__ = ["Planner"]

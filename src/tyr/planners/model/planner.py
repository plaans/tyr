import os
import resource
import shutil
import time
import traceback
import warnings
from dataclasses import replace
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from typing import Generator, Optional, Tuple

import psutil
import unified_planning.shortcuts as upf
from unified_planning.engines import PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.environment import get_environment
from unified_planning.exceptions import UPException
from unified_planning.grpc.proto_writer import ProtobufWriter
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.plans import PlanKind
from unified_planning.shortcuts import AbstractProblem, Engine

from tyr.core.paths import TyrPaths
from tyr.planners.database import Database
from tyr.planners.model.config import PlannerConfig, RunningMode, SolveConfig
from tyr.planners.model.pddl_planner import TyrPDDLPlanner
from tyr.planners.model.pddl_writer import TyrPDDLWriter
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems import ProblemInstance

warnings.filterwarnings("ignore", category=UserWarning)


# pylint: disable=too-many-branches
def terminate_process_tree(pid: Optional[int]) -> None:
    """Terminate a process and all its descendants."""

    try:
        parent = psutil.Process(pid)
        if not parent.is_running():
            return

        children = parent.children(recursive=True)

        # Terminate all children first in reverse order
        for child in reversed(children):
            try:
                if child.is_running():
                    child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Give them a brief moment to terminate before forcing a kill
        if children:
            alive = psutil.wait_procs(children, timeout=1)[1]

            for child in alive:
                try:
                    if child.is_running():
                        child.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        # Now handle the parent process
        try:
            if parent.is_running():
                parent.terminate()
                parent.wait(timeout=1)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                if parent.is_running():
                    parent.kill()
                    parent.wait(timeout=1)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
    except psutil.NoSuchProcess:
        pass  # Process already dead
    except Exception:  # pylint: disable=broad-exception-caught  # nosec: B110
        pass  # Silently ignore other errors


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

    def get_version_name(self, problem: ProblemInstance) -> str:
        """Get the version name for the given problem.

        Args:
            problem (ProblemInstance): The problem to solve.

        Returns:
            str: The version name to solve.
        """
        return self.config.problems.get(problem.domain.name, "base")

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
        version_name = self.get_version_name(problem)
        try:
            pb = problem.versions[version_name].value
            pb.name = problem.name
            return version_name, pb
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
                self,
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
        if version_name is None or version is None or version_name == "unsupported":
            # No version found, the problem is not supported.
            yield PlannerResult.unsupported(problem, self, config, running_mode)
            return

        # Clear the logs and logs the version to solve.
        shutil.rmtree(self.get_log_file(problem, "", running_mode).parent, True)
        self._log_problem_version(problem, version, running_mode)

        # Reload the version from the logs if it does not have control parameters.
        if "ctrl_params" not in version_name:
            dom_path = self.get_log_file(problem, "domain", running_mode, "pddl")
            prb_path = self.get_log_file(problem, "problem", running_mode, "pddl")
            version = PDDLReader().parse_problem(dom_path, prb_path)
            version.name = problem.name

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
            with builder(
                name=upf_planner_name,
                params=self.config.upf_params,
            ) as planner:
                # Disable compatibility checking.
                planner.skip_checks = True
                # Get the log file.
                log_path = self.get_log_file(problem, "output", running_mode)
                end = start + config.timeout
                self._last_upf_result = None
                # Use a multiprocessing queue to get the results from the child process.
                queue: Queue = Queue()
                process = Process(
                    target=solve_target,
                    args=(planner, version, config.timeout, log_path, queue),
                )
                process.start()
                start_process = time.time()
                # Get the results from the queue.
                while (
                    time.time() - start_process < config.timeout + config.timeout_offset
                ):
                    if not process.is_alive() and queue.empty():
                        break
                    try:
                        result = queue.get(timeout=0.1)
                        if isinstance(result, Exception):
                            # Enhanced error logging with context information
                            error_context = {
                                'planner': self.name,
                                'problem': problem.name if hasattr(problem, 'name') else str(problem),
                                'running_mode': running_mode.name if hasattr(running_mode, 'name') else str(running_mode),
                                'version_name': version_name,
                                'upf_planner_name': upf_planner_name,
                                'process_alive': process.is_alive(),
                                'queue_empty': queue.empty(),
                                'original_error_type': type(result).__name__,
                                'original_error_str': str(result)
                            }
                            
                            print(f"ERROR: Child process exception in {self.name}:")
                            print(f"  Problem: {error_context['problem']}")
                            print(f"  Mode: {error_context['running_mode']}")
                            print(f"  Version: {error_context['version_name']}")
                            print(f"  Process alive: {error_context['process_alive']}")
                            print(f"  Original error: {error_context['original_error_type']}: {error_context['original_error_str']}")
                            
                            # If the exception has a traceback, include it
                            if hasattr(result, '__traceback__') and result.__traceback__ is not None:
                                print(f"  Traceback from child process:")
                                traceback.print_exception(type(result), result, result.__traceback__)
                            
                            # Re-raise the original exception with added context
                            raise RuntimeError(
                                f"Child process error in {self.name} for problem {error_context['problem']} "
                                f"(mode: {error_context['running_mode']}): {error_context['original_error_type']}: {error_context['original_error_str']}"
                            ) from result
                        self._last_upf_result, start, end = result
                        if running_mode == RunningMode.ONESHOT:
                            break
                        yield self._handle_upf_result(
                            self.last_upf_result,
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
                    # Kill the entire process tree
                    terminate_process_tree(process.pid)
                    process.join(timeout=2)
                    # Return a timeout result if no result was found.
                    if self.last_upf_result is None and isinstance(
                        planner, TyrPDDLPlanner
                    ):
                        # pylint: disable=no-member
                        self._last_upf_result = planner.check_for_plan_from_files(
                            version,
                            str(log_path.parent),
                            anytime=running_mode == RunningMode.ANYTIME,
                        )
                    if self.last_upf_result is None:
                        yield PlannerResult.timeout(
                            problem,
                            self,
                            config,
                            running_mode,
                        )
                        return

            # Ensure process is properly joined
            if process is not None:
                try:
                    process.join(timeout=1)
                    if process.is_alive():
                        terminate_process_tree(process.pid)
                except Exception:  # pylint: disable=broad-exception-caught  # nosec: B110
                    pass

            if self.last_upf_result is None and isinstance(planner, TyrPDDLPlanner):
                # pylint: disable=no-member
                self._last_upf_result = planner.check_for_plan_from_files(
                    version,
                    str(log_path.parent),
                    anytime=running_mode == RunningMode.ANYTIME,
                )
            if self.last_upf_result is None:
                # No result was found.
                yield PlannerResult.timeout(
                    problem,
                    self,
                    config,
                    running_mode,
                )
                return
            yield self._handle_upf_result(
                self.last_upf_result,
                problem,
                version_name,
                running_mode,
                config,
                (start, end),
            )
            return

        except Exception:  # pylint: disable=broad-exception-caught
            # An error occurred...
            # Stop the process tree if it is still running.
            if process is not None and process.is_alive():
                terminate_process_tree(process.pid)
                process.join(timeout=2)
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
            pb = PDDLReader().parse_problem(dom_path, prb_path)
            b_writer = ProtobufWriter()
            pb_msg = b_writer.convert(pb)
            bin_path = self.get_log_file(problem, "problem", running_mode, "binpb")
            with open(bin_path, "wb") as file:
                file.write(pb_msg.SerializeToString())
        except Exception as error:
            err_path = self.get_log_file(problem, "bin_export_error", running_mode)
            err_path.write_text(str(error))

        # Export the problem in TXT format.
        txt_path = self.get_log_file(problem, "problem", running_mode, "txt")
        txt_path.write_text(str(version))

    def _solve_anytime(  # pylint: disable = too-many-arguments, too-many-positional-arguments
        self,
        planner: Engine,
        version: AbstractProblem,
        timeout: int,
        log_file_path: Path,
        queue: Queue,
    ) -> None:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            try:
                # Record time and try the solve the problem.
                start = time.time()
                for result in planner.get_solutions(
                    version,
                    timeout=float(timeout),
                    output_stream=log_file,
                ):
                    end = time.time()
                    if result.status != PlanGenerationResultStatus.TIMEOUT:
                        if (
                            result.plan is not None
                            and result.plan.kind == PlanKind.HIERARCHICAL_PLAN
                        ):
                            result.plan = result.plan.action_plan
                        queue.put((result, start, end))
            except Exception as error:  # pylint: disable=broad-exception-caught  # nosec: B110
                # Enhanced child process error reporting with full traceback
                import traceback as tb
                tb_lines = tb.format_exception(type(error), error, error.__traceback__)
                tb_string = ''.join(tb_lines)
                
                # Store comprehensive error information
                error_info = {
                    "type": error.__class__.__name__,
                    "module": error.__class__.__module__,
                    "message": str(error),
                    "args": error.args if hasattr(error, "args") else (),
                    "traceback": tb_string,
                    "planner_name": getattr(planner, 'name', 'unknown'),
                    "version_name": getattr(version, 'name', 'unknown'),
                    "timeout": timeout,
                    "method": "_solve_anytime"
                }
                
                # Log error in child process for immediate debugging
                print(f"ERROR in child process (_solve_anytime):")
                print(f"  Planner: {error_info['planner_name']}")
                print(f"  Version: {error_info['version_name']}")
                print(f"  Error: {error_info['type']}: {error_info['message']}")
                print(f"  Traceback:")
                print(tb_string)
                
                # Create a generic Exception with the error info
                picklable_error = Exception(f"{error.__class__.__name__}: {error}")
                setattr(picklable_error, "original_error_info", error_info)
                queue.put(picklable_error)

    def _solve_oneshot(  # pylint: disable = too-many-arguments, too-many-positional-arguments
        self,
        planner: Engine,
        version: AbstractProblem,
        timeout: int,
        log_file_path: Path,
        queue: Queue,
    ) -> None:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            try:
                # Record time and try the solve the problem.
                start = time.time()
                upf_result = planner.solve(
                    version,
                    timeout=float(timeout),
                    output_stream=log_file,
                )
                end = time.time()
                if (
                    upf_result.plan is not None
                    and upf_result.plan.kind == PlanKind.HIERARCHICAL_PLAN
                ):
                    upf_result.plan = upf_result.plan.action_plan
                queue.put((upf_result, start, end))
            except Exception as error:  # pylint: disable=broad-exception-caught  # nosec: B110
                # Enhanced child process error reporting with full traceback
                import traceback as tb
                tb_lines = tb.format_exception(type(error), error, error.__traceback__)
                tb_string = ''.join(tb_lines)
                
                # Store comprehensive error information
                error_info = {
                    "type": error.__class__.__name__,
                    "module": error.__class__.__module__,
                    "message": str(error),
                    "args": error.args if hasattr(error, "args") else (),
                    "traceback": tb_string,
                    "planner_name": getattr(planner, 'name', 'unknown'),
                    "version_name": getattr(version, 'name', 'unknown'),
                    "timeout": timeout,
                    "method": "_solve_oneshot"
                }
                
                # Log error in child process for immediate debugging
                print(f"ERROR in child process (_solve_oneshot):")
                print(f"  Planner: {error_info['planner_name']}")
                print(f"  Version: {error_info['version_name']}")
                print(f"  Error: {error_info['type']}: {error_info['message']}")
                print(f"  Traceback:")
                print(tb_string)
                
                # Create a generic Exception with the error info
                picklable_error = Exception(f"{error.__class__.__name__}: {error}")
                setattr(picklable_error, "original_error_info", error_info)
                queue.put(picklable_error)

    # pylint: disable = too-many-arguments, too-many-positional-arguments
    def _handle_upf_result(
        self,
        upf_result: PlanGenerationResult,
        problem: ProblemInstance,
        version_name: str,
        running_mode: RunningMode,
        config: SolveConfig,
        times: Tuple[float, float],
    ) -> PlannerResult:
        # Convert the result into inner format and set computation time if not present.
        result = PlannerResult.from_upf(
            self,
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
                if (res := callback(line)) is not None:  # pylint: disable=not-callable
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
        # Those domains have timed-initial literals that are not supported by LPG.
        til_domains = [
            "airport-time",
            "satellite-windows-time",
            "umts-time",
        ]
        # Those domains have required concurrency that are not supported by LPG.
        req_concurrency_domains = ["match-cellar"]

        if line in ["Max time exceeded.\n", "Error: max cpu-time reached\n"]:
            return PlannerResultStatus.TIMEOUT
        for domain in til_domains + req_concurrency_domains:
            if domain.upper() in line:
                return PlannerResultStatus.UNSUPPORTED
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

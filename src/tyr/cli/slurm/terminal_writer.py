import datetime
from pathlib import Path
from typing import List, Optional, TextIO, Union

from tyr.cli.collector import CollectionResult
from tyr.cli.writer import Writer
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.planner import Planner
from tyr.problems.model.instance import ProblemInstance


class SlurmTerminalWriter(Writer):
    """Utility class to write content of the slurm script on the terminal."""

    def __init__(
        self,
        solve_config: SolveConfig,
        out: Union[Optional[TextIO], List[TextIO]] = None,
        verbosity: int = 0,
        config: Optional[Path] = None,
    ) -> None:
        super().__init__(solve_config, out, verbosity, config)
        self._planners: List[Planner] = []
        self._problems: List[ProblemInstance] = []

    # ================================== Report ================================== #

    def report_collect(
        self,
        planners: CollectionResult[Planner],
        problems: CollectionResult[ProblemInstance],
    ) -> None:
        """Prints a report about the collection of planners and problems.

        Args:
            planners (CollectionResult[Planner]): The collection result on planners.
            problems (CollectionResult[ProblemInstance]): The collection result on problems.
        """

        if not self.quiet:
            self.rewrite("")
        self.report_collected(planners, "planner")
        self.report_collected(problems, "problem")

        self._planners = planners.selected
        self._problems = problems.selected

    # ================================== Session ================================= #

    def session_name(self) -> str:
        return "slurm"

    # =============================== Slurm Script =============================== #

    def mem_kilo(self) -> int:
        """Return the memory stored in the config in kilobytes."""
        return int(self._solve_config.memout / 1024)

    def script(
        self,
        user_mail: Optional[str],
        nodelist: List[str],
        running_modes: List[RunningMode],
    ) -> None:
        """Prints the slurm script."""
        num_pb = len(self._problems)
        num_jobs = len(self._planners) * num_pb
        if num_jobs == 0:
            self.line("No jobs to run.", red=True)
            return

        # Print the header of the script.
        self.line("#!/bin/bash")
        self.line("#SBATCH --job-name=tyr")
        self.line("#SBATCH --output=slurm_logs/%x-%j.out")
        self.line("#SBATCH --error=slurm_logs/%x-%j.err")
        if user_mail:
            self.line("#SBATCH --mail-type=ALL")
            self.line(f"#SBATCH --mail-user={user_mail}")
        self.line("#SBATCH --nodes=1")
        if nodelist:
            self.line(f"#SBATCH --nodelist={','.join(nodelist)}")
        self.line("#SBATCH --cpus-per-task=1")
        self.line(f"#SBATCH --mem-per-cpu={self.mem_kilo()}K")
        self.line(f"#SBATCH --array=0-{num_jobs-1}")

        # Print the planners list and the planner to use.
        self.write("\nPLANNERS=(")
        for i, planner in enumerate(sorted(self._planners, key=str)):
            if i > 0:
                self.write(" ")
            self.write(f'"{planner.name}$"')
        self.line(")")
        self.line("PLANNER_IDX=$((SLURM_ARRAY_TASK_ID % ${#PLANNERS[@]}))")
        self.line("PLANNER=${PLANNERS[$PLANNER_IDX]}")

        # Print the problem list and the problem to use.
        self.write("\nPROBLEMS=(")
        for i, problem in enumerate(sorted(self._problems, key=str)):
            if i > 0:
                self.write(" ")
            self.write(f'"{problem.name}$"')
        self.line(")")
        self.line("PROBLEM_IDX=$((SLURM_ARRAY_TASK_ID / ${#PLANNERS[@]}))")
        self.line("PROBLEM=${PROBLEMS[$PROBLEM_IDX]}")

        # Print the command to run.
        running_options = ""
        if RunningMode.ANYTIME in running_modes:
            running_options += " --anytime"
        if RunningMode.ONESHOT in running_modes:
            running_options += " --oneshot"
        unification = " --unify-epsilons" if self._solve_config.unify_epsilons else ""
        self.line("\necho \"==> Running '$PLANNER' on '$PROBLEM'\"")
        uid = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.line(
            " ".join(
                f"srun tyr.sif bench -p $PLANNER -d $PROBLEM --logs-path logs-{uid}/ "
                f"--db-path db-{uid}-${{SLURM_ARRAY_TASK_ID}}.sqlite3 "
                f"--timeout {self._solve_config.timeout} "
                f"--memout {self._solve_config.memout} "
                f"--verbose{running_options}{unification}"
                "".splitlines()
            )
        )


__all__ = ["SlurmTerminalWriter"]

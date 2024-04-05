from pathlib import Path
from typing import List, Optional, TextIO, Union

from tyr.cli.collector import CollectionResult
from tyr.cli.writter import Writter
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.planner import Planner
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.model.instance import ProblemInstance


class SlurmTerminalWritter(Writter):
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
        self._domains: List[AbstractDomain] = []

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

        self.rewrite("")
        self.report_collected(planners, "planner")
        self.report_collected(problems, "problem")

        self._planners = planners.selected
        self._domains = list({p.domain for p in problems.selected})

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
        num_jobs = len(self._planners) * len(self._domains)
        if num_jobs == 0:
            self.line("No jobs to run.", red=True)
            return

        # Print the header of the script.
        self.line("#!/bin/bash")
        self.line("#SBATCH --job-name=tyr")
        self.line("#SBATCH --output=%x-%j.out")
        self.line("#SBATCH --error=%x-%j.err")
        if user_mail:
            self.line("#SBATCH --mail-type=ALL")
            self.line(f"#SBATCH --mail-user={user_mail}")
        if nodelist:
            self.line(f"#SBATCH --nodes={min(len(nodelist), num_jobs)}")
            self.line(f"#SBATCH --nodelist={','.join(nodelist)}")
        else:
            # 5 is a total arbitrary number.
            self.line(f"#SBATCH --nodes={min(5, num_jobs)}")
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

        # Print the domains list and the domain to use.
        self.write("\nDOMAINS=(")
        for i, domain in enumerate(sorted(self._domains, key=str)):
            if i > 0:
                self.write(" ")
            self.write(f'"{domain.name}:"')
        self.line(")")
        self.line("DOMAIN_IDX=$((SLURM_ARRAY_TASK_ID / ${#PLANNERS[@]}))")
        self.line("DOMAIN=${DOMAINS[$DOMAIN_IDX]}")

        # Print the command to run.
        running_options = ""
        if RunningMode.ANYTIME in running_modes:
            running_options += " --anytime"
        if RunningMode.ONESHOT in running_modes:
            running_options += " --oneshot"
        self.line("\necho \"==> Running '$PLANNER' on '$DOMAIN'\"")
        self.line(
            " ".join(
                f"""srun tyr.sif bench -p $PLANNER -d $DOMAIN --logs-path logs/
--db-path db.sqlite3 --timeout {self._solve_config.timeout} --memout {self._solve_config.memout}
--verbose{running_options}""".splitlines()
            )
        )


__all__ = ["SlurmTerminalWritter"]

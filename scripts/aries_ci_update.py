import dataclasses
from pathlib import Path
import re
import subprocess  # nosec: B404
from typing import List

from unified_planning.shortcuts import PlanValidator, AbstractProblem, get_environment
from unified_planning.plans import Plan

from tyr.cli import collector
from tyr.cli.writer import Writer
from tyr.decorators.timeout_decorator import timeout
from tyr.planners.loader import register_all_planners
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems.model.instance import ProblemInstance


# ============================================================================ #
#                                   Constants                                  #
# ============================================================================ #

JOBS = 1
MEMOUT = 8 * 1024 * 1024 * 1024  # 8GB
TIMEOUT = 10
OVERALL_TIMEOUT = 30

PLANNER_RE = "^aries-base$"
PROBLEM_RE = "ipc.*:1$"

IGNORED = [
    "ipc2014-visit-all-sequential-agile",
    "ipc2014-visit-all-sequential-multi-core",
    "ipc2014-visit-all-sequential-optimal",
    "ipc2014-visit-all-sequential-satisficing",
]
ONLY: List[str] = []

# ============================================================================ #
#                                     Utils                                    #
# ============================================================================ #


def get_config() -> SolveConfig:
    """Return the configuration for the planner."""
    return SolveConfig(
        jobs=JOBS,
        memout=MEMOUT,
        timeout=TIMEOUT,
        timeout_offset=0,
        db_only=False,
        no_db_load=True,
        no_db_save=False,
        unify_epsilons=False,
    )


def extract_plan_for_val(plan: Path, domain: Path, problem: Path) -> Path:
    """Reformat a plan to be validated by Val."""

    domain_content = domain.read_text()
    problem_content = problem.read_text()

    def fix_upf_shit(name: str) -> str:
        name_alt = name.replace("-", "_")
        if name in domain_content or name in problem_content:
            return name
        if name_alt in domain_content or name_alt in problem_content:
            return name_alt
        raise ValueError(f"Name {name} not found in domain or problem")

    def format_line(line: str) -> str:
        if line.startswith(";"):
            return line

        regex = r"^\s*(?:(?P<time>\d+\.\d+):\s?)?(?P<name>[\w-]+)(?:\((?P<params>[\w, -]+)\))?\s?(?:\[(?P<duration>\d+\.\d+)\])?"  # pylint:disable=line-too-long # noqa: E501
        if not (match := re.match(regex, line)):
            return line
        groups = match.groupdict()

        res = ""

        if groups["time"]:
            res += f"{groups['time']}: "

        res += "("
        res += fix_upf_shit(groups["name"])
        if groups["params"]:
            res += " " + " ".join(map(fix_upf_shit, groups["params"].split(", ")))
        res += ")"
        if groups["duration"]:
            res += f" [{groups['duration']}]"
        return res

    lines = plan.read_text().splitlines()
    plan.with_suffix(".txt").write_text("\n".join(map(format_line, lines[1:])))
    return plan.with_suffix(".txt")


# pylint:disable=too-many-arguments
def report_results(
    tw: Writer,
    valid: list[ProblemInstance],
    invalid_for_aries: list[ProblemInstance],
    invalid_for_val: list[ProblemInstance],
    invalid_for_both: list[ProblemInstance],
):
    """Report the results of the validation."""
    tw.line()
    tw.big_separator("=", f"Valid: {len(valid)}", bold=True, green=True)
    tw.line()
    for problem in valid:
        tw.line(problem.name)

    tw.line()
    tw.big_separator(
        "=", f"Invalid for Aries: {len(invalid_for_aries)}", bold=True, red=True
    )
    tw.line()
    for problem in invalid_for_aries:
        tw.line(problem.name)

    tw.line()
    tw.big_separator(
        "=", f"Invalid for Val: {len(invalid_for_val)}", bold=True, red=True
    )
    tw.line()
    for problem in invalid_for_val:
        tw.line(problem.name)

    tw.line()
    tw.big_separator(
        "=", f"Invalid for both: {len(invalid_for_both)}", bold=True, red=True
    )
    tw.line()
    for problem in invalid_for_both:
        tw.line(problem.name)


def save_results(
    problems: list[ProblemInstance],
    valid: list[ProblemInstance],
    invalid_for_aries: list[ProblemInstance],
    invalid_for_val: list[ProblemInstance],
    invalid_for_both: list[ProblemInstance],
):
    """Save the results of the validation."""
    in_logs = Path(__file__).parent.parent / "logs/aries-base"
    out_logs = Path(__file__).parent.parent / "logs/aries-ci-update"

    for problem in problems:
        in_log = in_logs / problem.domain.name / "1-oneshot"
        if not in_log.exists():
            continue

        if problem in valid:
            out_log = out_logs / "valid" / problem.domain.name
        elif problem in invalid_for_aries:
            out_log = out_logs / "invalid_for_aries" / problem.domain.name
        elif problem in invalid_for_val:
            out_log = out_logs / "invalid_for_val" / problem.domain.name
        elif problem in invalid_for_both:
            out_log = out_logs / "invalid_for_both" / problem.domain.name
        else:
            out_log = out_logs / "unsolved" / problem.domain.name

        out_log.mkdir(parents=True, exist_ok=True)
        for file in in_log.iterdir():
            file.rename(out_log / file.name)


def solve(
    planner: Planner, problem: ProblemInstance, config: SolveConfig
) -> PlannerResult:
    """Solve a problem with a planner."""

    @timeout(OVERALL_TIMEOUT)
    def _solve():
        return planner.solve_single(problem, config, RunningMode.ONESHOT)

    timeout_result = PlannerResult.timeout(
        problem,
        planner,
        dataclasses.replace(config, timeout=OVERALL_TIMEOUT),
        RunningMode.ONESHOT,
    )
    try:
        return _solve() or timeout_result
    except TimeoutError:
        return timeout_result


def validate_plan_with_aries(problem: AbstractProblem, plan: Plan) -> bool:
    """Validate a plan using Aries Validator."""
    with PlanValidator(name="aries-val") as validator:
        return validator.validate(problem, plan)


def validate_plan_with_val(problem: Path, domain: Path, plan: Path) -> bool:
    """Validate a plan using Val."""
    cmd = (
        "./src/tyr/planners/planners/aries/planning/ext/val-pddl "
        f"{domain.as_posix()} {problem.as_posix()} {plan.as_posix()}"
    )
    return subprocess.run(cmd, shell=True, check=False).returncode == 0  # nosec: B602


# ============================================================================ #
#                                     Main                                     #
# ============================================================================ #


# pylint:disable=too-many-locals, too-many-branches, too-many-statements
def main():
    """Main function."""

    # UPF environment
    env = get_environment()
    env.error_used_name = False

    # Load the configuration
    config = get_config()
    tw = Writer(config)
    tw.report_solve_config()

    # Load the planner and register it into UPF
    planners = collector.collect_planners(PLANNER_RE)
    tw.report_collected(planners, "planner")
    planner = planners.selected[0]
    register_all_planners()

    # Load the problems
    problems = collector.collect_problems(PROBLEM_RE)
    tw.report_collected(problems, "problem")
    problems = sorted(problems.selected, key=lambda p: p.name)
    for problem in problems:
        tw.line(f"  - {problem.name}")

    # Initialize the lists
    valid = []
    invalid_for_aries = []
    invalid_for_val = []
    invalid_for_both = []

    try:
        for i, problem in enumerate(problems):
            # Ignore the problem if it is in the ignored list or not in the only list
            if problem.domain.name in IGNORED or (
                len(ONLY) > 0 and problem.domain.name not in ONLY
            ):
                continue

            # Solve the problem
            tw.line()
            pct = int((i + 1) / len(problems) * 100)
            tw.separator("*", f"Problem {problem.name} ({pct}%)", bold=True, blue=True)
            result = solve(planner, problem, config)
            tw.line(f"\nStatus: {result.status}\n", bold=True)

            # The problem was solved, validate the plan
            if result.status == PlannerResultStatus.SOLVED:
                # Validation by Aries Validator
                if result_val := validate_plan_with_aries(
                    result.problem.versions["base"].value, result.plan
                ):
                    tw.line("Plan validated by Aries\n", green=True)
                    aries_valid = True
                else:
                    tw.line(
                        "\n  ".join(map(lambda m: m.message, result_val.log_messages))
                    )
                    tw.line("Plan validation failed by Aries\n", red=True)
                    aries_valid = False

                # Validation by Val
                log_path = (
                    Path(__file__).parent.parent
                    / f"logs/aries-base/{problem.domain.name}/1-oneshot"
                )
                pb = log_path / "problem.pddl"
                dm = log_path / "domain.pddl"
                pl = log_path / "plan.log"
                pl = extract_plan_for_val(pl, dm, pb)
                if validate_plan_with_val(pb, dm, pl):
                    tw.line("Plan validated by Val", green=True)
                    val_valid = True
                else:
                    tw.line("Plan validation failed by Val", red=True)
                    val_valid = False

                # Update the lists
                if aries_valid and val_valid:
                    valid.append(problem)
                elif aries_valid and not val_valid:
                    invalid_for_val.append(problem)
                elif val_valid and not aries_valid:
                    invalid_for_aries.append(problem)
                elif not aries_valid and not val_valid:
                    invalid_for_both.append(problem)
                else:
                    raise ValueError("This should not happen")

            # The resolution failed with an error
            elif result.status == PlannerResultStatus.ERROR:
                tw.line(result.error_message, red=True)

            # The resolution failed with no plan
            else:
                tw.line("No plan available", yellow=True)

    # Handle the keyboard interruption and handle the results
    except KeyboardInterrupt:
        pass
    finally:
        save_results(
            problems,
            valid,
            invalid_for_aries,
            invalid_for_val,
            invalid_for_both,
        )
        report_results(
            tw,
            valid,
            invalid_for_aries,
            invalid_for_val,
            invalid_for_both,
        )

        tw.line()
        tw.big_separator("=", "End", bold=True)
        tw.line()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

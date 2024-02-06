from pathlib import Path
from typing import Optional

import unified_planning as up
from unified_planning.model.scheduling.scheduling_problem import SchedulingProblem
from unified_planning.shortcuts import LE, AbstractProblem

from tyr.problems.model import AbstractDomain, ProblemInstance


class Problem:
    def __init__(self) -> None:
        self.jobs: list[int] = []
        self.res: list[int] = []
        self.horizon = -1

        self.succs: dict[int, list[int]] = {}
        self.durations: list[int] = []
        self.demands: list[list[int]] = []
        self.capacities: list[int] = []


def ints(strs):
    return [int(s) for s in strs]


# def myset(prefix, cardinality):
#    return [f'{prefix}{i+1}' for i in range(cardinality)]


def myset(cardinality):
    return list(range(1, cardinality + 1))


def index_of_line(lines, substr):
    return next(i for i, line in enumerate(lines) if substr in line)


def rhs_part(lines, prefix):
    return lines[index_of_line(lines, prefix)].split(":")[1]


# def succs_from_line(line): return [ f'j{j}' for j in line.split()[3:] ]


def succs_from_line(line):
    return [int(j) for j in line.split()[3:]]


def column(lines, col, rowStart, rowCount):
    return [
        int(lines[rowIx].split()[col]) for rowIx in range(rowStart, rowStart + rowCount)
    ]


def PSPLIB_parser(filepath):
    # --------------------------------
    # Python parser for PSPLIB files
    # input: filepath to PSPLIB file
    # output: lists of all the data
    #         in following order:
    #         njobs, nperiods, jobs, res, periods, succs, durations, demands, capacities
    # --------------------------------
    with open(filepath, encoding="utf-8") as fp:
        lines = fp.readlines()

    njobs = int(rhs_part(lines, "jobs (incl. supersource"))

    nres = int(rhs_part(lines, "- renewable").split()[0])
    nperiods = int(rhs_part(lines, "horizon"))
    prec_offset = index_of_line(lines, "PRECEDENCE RELATIONS:") + 2
    attrs_offset = index_of_line(lines, "REQUESTS/DURATIONS") + 3
    caps_offset = index_of_line(lines, "RESOURCEAVAILABILITIES") + 2

    # jobs, res, periods = myset('j', njobs), myset('r', nres), myset('t', nperiods)
    problem = Problem()
    problem.jobs = myset(njobs)
    problem.res = myset(nres)
    problem.horizon = nperiods

    problem.succs = {
        j: succs_from_line(lines[prec_offset + ix]) for ix, j in enumerate(problem.jobs)
    }
    problem.durations = column(lines, 2, attrs_offset, njobs)
    problem.demands = [
        ints(lines[ix].split()[3:]) for ix in range(attrs_offset, attrs_offset + njobs)
    ]
    problem.capacities = ints(lines[caps_offset].split())

    return problem


# pylint: disable = too-many-locals
def encode(problem: Problem):
    u = SchedulingProblem("rcpsp")

    resources = {}
    for idx, r in enumerate(problem.res):
        capacity = problem.capacities[idx]
        resources[r] = u.add_resource(name=f"r{r}", capacity=capacity)

    activities = {}
    for idx, job in enumerate(problem.jobs):
        duration = problem.durations[idx]
        a = u.add_activity(f"a{job}", duration=duration)
        for res_idx, demand in enumerate(problem.demands[idx]):
            res = problem.res[res_idx]
            fluent = resources[res]
            if demand != 0:
                a.uses(fluent, demand)
        activities[job] = a

    for job, succs in problem.succs.items():
        act = activities[job]
        for succ_job in succs:
            succ_act = activities[succ_job]
            act.add_constraint(LE(act.end, succ_act.start))

    u.add_quality_metric(up.model.MinimizeMakespan())

    return u


FOLDER = Path(__file__).parent.resolve() / "base"


class RcpspSchedulingDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        if int(problem.uid) > self.get_num_problems():
            return None

        return encode(PSPLIB_parser(FOLDER / f"instance-{problem.uid}.sm"))

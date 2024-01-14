from pathlib import Path

import pytest
import unified_planning.model.htn.task
from unified_planning.io import PDDLReader

from tyr import goals_to_tasks


class TestConverter:
    @pytest.mark.parametrize("problem_id", ["01", "02", "03"])
    def test_goals_to_tasks(self, problem_id: str):
        base_folder = Path(__file__).parent.resolve() / "fixtures/pddl"
        base_dom = base_folder / "domain.pddl"
        base_ins = base_folder / f"instance-{problem_id}.pddl"
        base_pb = PDDLReader().parse_problem(base_dom.as_posix(), base_ins.as_posix())

        unified_planning.model.htn.task._task_id_counter = 0
        hier_folder = Path(__file__).parent.resolve() / "fixtures/hddl"
        hier_dom = hier_folder / "domain.hddl"
        hier_ins = hier_folder / f"instance-{problem_id}.hddl"
        hier_pb = PDDLReader().parse_problem(hier_dom.as_posix(), hier_ins.as_posix())

        mapping = {"at": "go"}
        unified_planning.model.htn.task._task_id_counter = 0
        result = goals_to_tasks(base_pb, hier_dom, mapping)

        assert str(result) == str(hier_pb)

    def test_goals_to_tasks_wrong_domain(self):
        base_folder = Path(__file__).parent.resolve() / "fixtures/pddl"
        base_dom = base_folder / "domain.pddl"
        base_ins = base_folder / "instance-01.pddl"
        base_pb = PDDLReader().parse_problem(base_dom.as_posix(), base_ins.as_posix())

        mapping = {"at": "go"}
        with pytest.raises(ValueError):
            goals_to_tasks(base_pb, base_dom, mapping)

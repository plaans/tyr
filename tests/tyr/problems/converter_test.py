from pathlib import Path

import pytest
import unified_planning.model.htn.task
from unified_planning.io import PDDLReader

from tyr import goals_to_tasks


class TestConverter:
    @staticmethod
    @pytest.fixture()
    def base_problem(request):
        base_folder = Path(__file__).parent.resolve() / "fixtures/pddl"
        base_dom = base_folder / "domain.pddl"
        base_ins = base_folder / f"instance-{request.param}.pddl"
        yield (
            request.param,
            PDDLReader().parse_problem(base_dom.as_posix(), base_ins.as_posix()),
        )

    @staticmethod
    @pytest.fixture()
    def hier_domain():
        yield Path(__file__).parent.resolve() / "fixtures/hddl/domain.hddl"

    @staticmethod
    @pytest.fixture()
    def mapping():
        yield {"at": "go"}

    @pytest.mark.parametrize("base_problem", ["01", "02", "03"], indirect=True)
    def test_goals_to_tasks(self, base_problem, hier_domain, mapping):
        unified_planning.model.htn.task._task_id_counter = 0
        hier_instance = hier_domain.parent / f"instance-{base_problem[0]}.hddl"
        hier_pb = PDDLReader().parse_problem(
            hier_domain.as_posix(),
            hier_instance.as_posix(),
        )

        unified_planning.model.htn.task._task_id_counter = 0
        result = goals_to_tasks(base_problem[1], hier_domain, mapping)

        assert str(result) == str(hier_pb)

    @pytest.mark.parametrize("base_problem", ["01", "02", "03"], indirect=True)
    def test_goals_to_tasks_wrong_domain(self, base_problem, hier_domain, mapping):
        base_domain = hier_domain.parent.parent / "pddl/domain.pddl"
        with pytest.raises(ValueError):
            goals_to_tasks(base_problem[1], base_domain, mapping)

    @pytest.mark.parametrize("base_problem", ["01", "02", "03"], indirect=True)
    def test_goals_are_copied(self, base_problem, hier_domain, mapping):
        assert len(base_problem[1].goals) > 0
        goals_to_tasks(base_problem[1], hier_domain, mapping)
        assert len(base_problem[1].goals) > 0

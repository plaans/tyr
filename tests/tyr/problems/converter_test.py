from pathlib import Path
from unittest.mock import Mock

import pytest
import unified_planning.model.htn.task
from unified_planning.shortcuts import Problem
from unified_planning.io import PDDLReader

from tyr import get_goals, goals_to_tasks


@pytest.fixture(scope="module")
def base_problem(request):
    base_folder = Path(__file__).parent.resolve() / "fixtures/pddl"
    base_dom = base_folder / "domain.pddl"
    base_ins = base_folder / f"instance-{request.param}.pddl"
    yield (
        request.param,
        PDDLReader().parse_problem(base_dom.as_posix(), base_ins.as_posix()),
    )


@pytest.fixture(scope="module")
def hier_domain():
    yield Path(__file__).parent.resolve() / "fixtures/hddl/domain.hddl"


@pytest.fixture(scope="module")
def mapping():
    yield {"at": "go"}


class TestConverter:
    def test_get_goals(self):
        problem = Mock(spec=Problem)
        goal1 = Mock()
        goal2 = Mock()
        goal3 = Mock()
        goal4 = Mock()
        goal5 = Mock()
        goal6 = Mock()
        goal1.is_and.return_value = True
        goal1.args = [goal2, goal3]
        goal2.is_and.return_value = False
        goal3.is_and.return_value = True
        goal3.args = [goal4, goal5, goal6]
        goal4.is_and.return_value = False
        goal5.is_and.return_value = False
        goal6.is_and.return_value = False
        problem.goals = [goal1]

        result = get_goals(problem)
        assert set(result) == {goal2, goal4, goal5, goal6}

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

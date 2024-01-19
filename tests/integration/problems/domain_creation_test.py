import pytest
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.model.scheduling import SchedulingProblem
from unified_planning.shortcuts import AbstractProblem

from tests.integration.problems.domains import FakeDomain
from tyr import AbstractDomain, get_all_domains


class TestDomainCreation:
    @pytest.mark.parametrize(
        ["problem_id", "is_none"],
        [(str(i).zfill(2), not (0 < i <= 3)) for i in range(15)],
    )
    @pytest.mark.parametrize("version_name", ["a_first", "base", "modified"])
    def test_fake_domain_problem_creation(
        self,
        problem_id: str,
        is_none: bool,
        version_name: str,
    ):
        domain = FakeDomain()
        problem = domain.get_problem(problem_id)
        version = problem.versions[version_name]
        assert (version.value is None) == is_none
        if not is_none:
            assert isinstance(version.value, AbstractProblem)

    @pytest.mark.slow
    @pytest.mark.parametrize(
        ["domain", "problem_id"],
        [
            (d, f"{p:0>2}")
            for d in get_all_domains()
            for p in range(1, d.get_num_problems() + 2)
            # Test one more problem (+2) in order to check behaviour on non existant problem
        ],
        ids=lambda x: x if isinstance(x, str) else x.name,
    )
    def test_real_domain_creation(self, domain: AbstractDomain, problem_id: str):
        problem = domain.get_problem(problem_id)
        assert (
            problem is not None
        ), f"The domain {domain.name} is empty, please consider to remove it"
        # Check all versions can successfully be built.
        for version_name, version in problem.versions.items():
            print(f"Checking version {version_name}")
            value = version.value  # Check the value can be accessed without error.
            if value is not None:
                # Check the problems have goals to achieve.
                if isinstance(value, HierarchicalProblem):
                    assert len(value.task_network.subtasks) != 0
                elif isinstance(value, SchedulingProblem):
                    assert len(value.activities) != 0
                else:
                    assert len(value.goals) != 0
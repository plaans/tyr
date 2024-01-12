import pytest
from unified_planning.shortcuts import AbstractProblem

from tests.integration.problem.domains import FakeDomain


class TestDomainCreation:
    @pytest.mark.parametrize(
        ["problem_id", "is_none"],
        [(str(i).zfill(2), not (0 < i <= 3)) for i in range(15)],
    )
    @pytest.mark.parametrize("version_name", ["a_first", "base", "modified"])
    def test_problem_creation(
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

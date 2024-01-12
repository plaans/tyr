from unittest.mock import patch

import pytest
from unified_planning.shortcuts import AbstractProblem

import tests.integration.problem.variants as variant_module
from tests.integration.problem.domains import FakeDomain


class TestDomainCreation:
    @patch("tyr.problem", variant_module)
    @pytest.mark.parametrize("variant_name", ["hierarchical", "sequential"])
    @pytest.mark.parametrize(
        ["problem_id", "is_none"],
        [(str(i).zfill(2), not (0 < i <= 3)) for i in range(15)],
    )
    @pytest.mark.parametrize("version_name", ["a_first", "base", "modified"])
    def test_problem_creation(
        self,
        variant_name: str,
        problem_id: str,
        is_none: bool,
        version_name: str,
    ):
        domain = FakeDomain()
        problem = domain.get_problem(variant_name, problem_id)
        version = problem.versions[version_name]
        assert (version.value is None) == is_none
        if not is_none:
            assert isinstance(version.value, AbstractProblem)

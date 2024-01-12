from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from tests.utils import ModelTest
from tyr import ProblemInstance


class TestProblem(ModelTest):
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    def get_default_attributes(self) -> Dict[str, Any]:
        return {
            "_uid": "05",
            "_domain": self.domain(),
            "_versions": dict(),
        }

    def get_instance(self) -> ProblemInstance:
        return ProblemInstance(self.domain(), "05")

    def domain(self):
        if not hasattr(self, "_domain"):
            self._domain = MagicMock()
            self._domain.name = "mockdomain"
        return self._domain

    @pytest.fixture()
    def problem(self, request):
        problem = self.get_instance()
        problem._versions = {"base": MagicMock()}

        def teardown():
            problem._versions = {"base": MagicMock()}

        request.addfinalizer(teardown)
        yield problem

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    def test_get_name(self, problem: ProblemInstance):
        expected = "mockdomain:05"
        assert problem.name == expected

    def test_is_empty(self, problem: ProblemInstance):
        problem._versions.clear()
        assert problem.is_empty

    def test_is_not_empty(self, problem: ProblemInstance):
        assert not problem.is_empty

    def test_add_version(self, problem: ProblemInstance):
        problem._versions.clear()
        version = MagicMock()
        problem.add_version("version", version)
        assert problem.versions == {"version": version}

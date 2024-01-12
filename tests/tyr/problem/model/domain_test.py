from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from pyparsing import ParseException
from unified_planning.shortcuts import AbstractProblem

import tests.tyr.problem.model.variant_test as variant_module
from tests.utils import AbstractSingletonModelTest
from tyr import AbstractDomain, AbstractVariant, ProblemInstance


class MockdomainDomain(AbstractDomain):
    def build_mockvariant_problem_base(self, problem: ProblemInstance):
        return MagicMock()

    def build_mockvariant_problem_no_speed(self, problem: ProblemInstance):
        return MagicMock()


class TestAbstractDomain(AbstractSingletonModelTest):
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    def get_default_attributes(self) -> Dict[str, Any]:
        return {
            "_name": "mockdomain",
            "_variants": dict(),
        }

    def get_abstract_instance(self) -> AbstractDomain:
        return AbstractDomain()

    def get_instance(self) -> AbstractDomain:
        return MockdomainDomain()

    @pytest.fixture()
    def domain(self, request):
        domain = self.get_instance()

        def teardown():
            domain._variants.clear()

        request.addfinalizer(teardown)
        yield domain

    @staticmethod
    @pytest.fixture()
    def variant(request, problem):
        variant_patch = patch(
            "tyr.problem.model.variant.AbstractVariant",
            autospec=True,
        )
        variant = variant_patch.start()
        variant.get_problem.return_value = problem
        variant.name = "mockvariant"
        request.addfinalizer(variant_patch.stop)
        yield variant

    @staticmethod
    @pytest.fixture()
    def problem():
        yield MagicMock()

    @staticmethod
    @pytest.fixture()
    def files_path(request):
        yield Path(__file__).parent / "fixtures" / request.param

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    # ================================ Get problem =============================== #

    @pytest.mark.parametrize("problem_id", ["01", "05", "13"])
    def test_get_problem_from_present_variant(
        self,
        domain: AbstractDomain,
        variant: AbstractVariant,
        problem: Mock,
        problem_id: str,
    ):
        domain._variants = {variant.name: variant}
        result = domain.get_problem(variant.name, problem_id)
        # Check the result is correct.
        assert result == problem
        # Check the right parameters have been given.
        variant.get_problem.assert_called_once_with(problem_id)

    @patch("tyr.problem", variant_module)
    @patch(f"{variant_module.__name__}.MockvariantVariant", autospec=True)
    def test_get_problem_from_absent_variant(
        self,
        mockvariant: AbstractVariant,
        domain: AbstractDomain,
    ):
        mockvariant.name = "mockvariant"
        result = domain.get_problem(mockvariant.name, "01")
        # Check the variant has been created.
        assert mockvariant.name in domain.variants
        # Check the constructor has been called with the right parameters.
        mockvariant.assert_called_once_with(
            domain,
            [
                domain.build_mockvariant_problem_base,
                domain.build_mockvariant_problem_no_speed,
            ],
        )
        # Check a problem has been returned.
        assert result is not None

    def test_get_problem_from_unexistant_variant(
        self,
        domain: AbstractDomain,
        variant: AbstractVariant,
    ):
        result = domain.get_problem(variant.name, "01")
        # Check nothing has been returned.
        assert result is None

    @patch("tyr.problem", variant_module)
    @patch(f"{variant_module.__name__}.UnsupportedvariantVariant", autospec=True)
    def test_get_problem_from_unsupported_variant(
        self,
        mockvariant: AbstractVariant,
        domain: AbstractDomain,
    ):
        mockvariant.name = "unsupportedvariant"
        result = domain.get_problem(mockvariant.name, "01")
        # Check nothing has been returned.
        assert result is None

    # ============================== Load from files ============================= #

    @patch("builtins.open")
    @pytest.mark.parametrize("problem_id", [str(i).zfill(2) for i in range(15)])
    @pytest.mark.parametrize("files_path", ["hddl", "pddl"], indirect=True)
    def test_load_from_files_reads_domain(
        self,
        mock_open: Mock,
        domain: AbstractDomain,
        files_path: Path,
        problem_id: str,
    ):
        extension = files_path.name
        domain_file = (files_path / f"domain.{extension}").resolve()

        # Raises a ParseException because of the patch of builtins.open
        try:
            domain.load_from_files(files_path, problem_id)
            mock_open.assert_not_called()
        except ParseException:
            mock_open.assert_any_call(domain_file.as_posix(), "r")

    @patch("builtins.open")
    @pytest.mark.parametrize("problem_id", [str(i).zfill(2) for i in range(15)])
    @pytest.mark.parametrize("files_path", ["hddl", "pddl"], indirect=True)
    def test_load_from_files_reads_problem(
        self,
        mock_open: Mock,
        domain: AbstractDomain,
        files_path: Path,
        problem_id: str,
    ):
        extension = files_path.name
        problem_file = (files_path / f"instance-{problem_id}.{extension}").resolve()

        # Raises a ParseException because of the patch of builtins.open
        try:
            domain.load_from_files(files_path, problem_id)
            mock_open.assert_not_called()
        except ParseException:
            mock_open.assert_any_call(problem_file.as_posix(), "r")

    @pytest.mark.parametrize(
        ["problem_id", "is_none"],
        [(f"{i:0>2}", not (0 < i <= 3)) for i in range(15)],
        ids=[f"{i:0>2}-{'Some' if (0 < i <= 3) else 'None'}" for i in range(15)],
    )
    @pytest.mark.parametrize("files_path", ["hddl", "pddl"], indirect=True)
    def test_load_from_files_result(
        self,
        domain: AbstractDomain,
        files_path: Path,
        problem_id: str,
        is_none: bool,
    ):
        result = domain.load_from_files(files_path, problem_id)
        assert (result is None) == is_none
        if not is_none:
            assert isinstance(result, AbstractProblem)

from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from pyparsing import ParseException
from unified_planning.shortcuts import AbstractProblem

from tests.utils import AbstractSingletonModelTest
from tyr import AbstractDomain, Lazy, ProblemInstance


class MockdomainDomain(AbstractDomain):
    def build_problem_base(self, problem: ProblemInstance):
        if int(problem.uid) > 0:
            return MagicMock()
        return None

    def build_problem_no_speed(self, problem: ProblemInstance):
        if int(problem.uid) > 0:
            return MagicMock()
        return None


class EmptyDomain(AbstractDomain):
    pass


class TestAbstractDomain(AbstractSingletonModelTest):
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    def get_default_attributes(self) -> Dict[str, Any]:
        return {
            "_name": "mockdomain",
            "_problems": dict(),
        }

    def get_abstract_instance(self) -> AbstractDomain:
        return AbstractDomain()

    def get_instance(self) -> AbstractDomain:
        return MockdomainDomain()

    @pytest.fixture()
    def domain(self, request):
        domain = self.get_instance()

        def teardown():
            domain._problems.clear()

        request.addfinalizer(teardown)
        yield domain

    @pytest.fixture()
    def empty_domain(self):
        yield EmptyDomain()

    @pytest.fixture()
    def tracked_domain(self, request):
        domain = Mock(MockdomainDomain)
        domain.get_problem = lambda x: MockdomainDomain.get_problem(domain, x)

        def teardown():
            domain.problems.clear()

        request.addfinalizer(teardown)
        yield domain

    @pytest.fixture()
    def tracked_domain_version(self, request):
        domain = Mock(MockdomainDomain)
        domain.get_problem_version = lambda x, y: MockdomainDomain.get_problem_version(
            domain, x, y
        )

        def teardown():
            domain.problems.clear()

        request.addfinalizer(teardown)
        yield domain

    @staticmethod
    @pytest.fixture()
    def problem(request, domain):
        return ProblemInstance(domain, request.param)

    @staticmethod
    @pytest.fixture()
    def files_path(request):
        yield Path(__file__).parent.parent / "fixtures" / request.param

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    # =============================== Build problem ============================== #

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_build_problem_version_names(self, domain: AbstractDomain, problem_id: str):
        problem = domain.build_problem(problem_id)
        assert list(problem.versions.keys()) == ["base", "no_speed"]

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    @pytest.mark.parametrize("version", ["base", "no_speed"])
    def test_build_problem_version_values(
        self,
        domain: AbstractDomain,
        problem_id: str,
        version: str,
    ):
        problem = domain.build_problem(problem_id)
        if problem_id == "-02":
            assert problem.versions[version].value is None
        else:
            assert isinstance(problem.versions[version].value, MagicMock)

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_build_problem_no_factories(
        self,
        empty_domain: AbstractDomain,
        problem_id: str,
    ):
        problem = empty_domain.build_problem(problem_id)
        assert problem is None

    # =============================== Save to cache ============================== #

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    def test_save_problem_to_empty_cache(
        self,
        domain: AbstractDomain,
        problem: ProblemInstance,
    ):
        assert domain._problems == dict()
        domain.save_problem_to_cache(problem)
        assert domain._problems == {problem.uid: problem}
        domain.save_problem_to_cache(problem)
        assert domain._problems == {problem.uid: problem}

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    def test_save_problem_to_non_empty_cache(
        self,
        domain: AbstractDomain,
        problem: ProblemInstance,
    ):
        base_problem = MagicMock()
        domain._problems = {"213": base_problem}
        domain.save_problem_to_cache(problem)
        assert domain._problems == {"213": base_problem, problem.uid: problem}

    def test_save_null_problem_to_cache(self, domain: AbstractDomain):
        domain.save_problem_to_cache(None)
        assert domain._problems == dict()

    # ============================== Load from cache ============================= #

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    def test_get_present_problem_from_cache(
        self,
        domain: AbstractDomain,
        problem: ProblemInstance,
    ):
        domain.save_problem_to_cache(problem)
        result = domain.load_problem_from_cache(problem.uid)
        assert result == problem

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_get_absent_problem_from_cache(
        self,
        domain: AbstractDomain,
        problem_id: str,
    ):
        result = domain.load_problem_from_cache(problem_id)
        assert result is None

    # ================================ Get problem =============================== #

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    def test_get_problem_load_from_cache(
        self,
        tracked_domain: AbstractDomain,
        problem: ProblemInstance,
    ):
        tracked_domain._problems = {"13": MagicMock()}
        tracked_domain.get_problem(problem.uid)
        tracked_domain.load_problem_from_cache.assert_called_once_with(problem.uid)

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    def test_get_problem_save_to_cache(
        self,
        tracked_domain: AbstractDomain,
        problem: ProblemInstance,
    ):
        tracked_domain._problems = {"13": MagicMock()}
        tracked_domain.get_problem(problem.uid)
        tracked_domain.save_problem_to_cache.assert_called_once()

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    def test_get_present_problem(
        self,
        tracked_domain: AbstractDomain,
        problem: ProblemInstance,
    ):
        tracked_domain.load_problem_from_cache = (
            lambda x: MockdomainDomain.load_problem_from_cache(tracked_domain, x)
        )
        tracked_domain.problems = {problem.uid: problem}
        result = tracked_domain.get_problem(problem.uid)
        assert result == problem
        tracked_domain.build_problem.assert_not_called()

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    def test_get_absent_problem(
        self,
        tracked_domain: AbstractDomain,
        problem: ProblemInstance,
    ):
        tracked_domain.load_problem_from_cache = (
            lambda x: MockdomainDomain.load_problem_from_cache(tracked_domain, x)
        )
        tracked_domain.problems = dict()
        result = tracked_domain.get_problem(problem.uid)
        assert result is not None
        tracked_domain.build_problem.assert_called_once_with(problem.uid)

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_get_problem_versions_are_lazy(
        self,
        domain: AbstractDomain,
        problem_id: str,
    ):
        result = domain.get_problem(problem_id)
        assert all(isinstance(v, Lazy) for v in result.versions.values())

    # ============================ Get problem version =========================== #

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    @pytest.mark.parametrize("version", ["base", "no_speed"])
    def test_get_problem_version_call_get_problem(
        self,
        tracked_domain_version: AbstractDomain,
        problem_id: str,
        version: str,
    ):
        # Raises a ParseException because of the mock of get_problem
        with pytest.raises(TypeError):
            tracked_domain_version.get_problem_version(problem_id, version)
            tracked_domain_version.get_problem.assert_called_once_with(problem_id)

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    @pytest.mark.parametrize("version", ["base", "no_speed"])
    def test_get_problem_version_value(
        self,
        tracked_domain_version: AbstractDomain,
        problem: ProblemInstance,
        version: str,
    ):
        factory = getattr(tracked_domain_version, f"build_problem_{version}")
        problem.add_version(version, Lazy(factory))
        tracked_domain_version.get_problem.return_value = problem
        result = tracked_domain_version.get_problem_version(problem.uid, version)
        assert result == problem.versions[version].value

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    @pytest.mark.parametrize("version", ["base", "no_speed"])
    def test_get_problem_version_of_null_problem(
        self,
        tracked_domain_version: AbstractDomain,
        problem_id: str,
        version: str,
    ):
        tracked_domain_version.get_problem.return_value = None
        result = tracked_domain_version.get_problem_version(problem_id, version)
        assert result is None

    @pytest.mark.parametrize("problem", ["01", "05", "-02"], indirect=True)
    @pytest.mark.parametrize("version", ["not_present", "inexistant"])
    def test_get_problem_version_inexistant(
        self,
        tracked_domain_version: AbstractDomain,
        problem: ProblemInstance,
        version: str,
    ):
        tracked_domain_version.get_problem.return_value = problem
        result = tracked_domain_version.get_problem_version(problem.uid, version)
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

from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

from tests.utils import AbstractModelTest
from tyr import AbstractVariant, Lazy, Problem


class MockvariantVariant(AbstractVariant):
    pass


class TrackedvariantVariant(AbstractVariant):
    def __init__(self, domain, problem_factories) -> None:
        super().__init__(domain, problem_factories)
        self.from_cache_count = 0
        self.save_cache_count = 0
        self.build_count = 0

    def get_problem_from_cache(self, problem_id: str) -> Optional[Problem]:
        self.from_cache_count += 1
        return super().get_problem_from_cache(problem_id)

    def save_problem_to_cache(self, problem: Problem) -> None:
        self.save_cache_count += 1
        return super().save_problem_to_cache(problem)

    def build_problem(self, uid: str) -> None:
        self.build_count += 1
        return super().build_problem(uid)


class UnsupportedvariantVariant(AbstractVariant):
    pass


class TestAbstractVariant(AbstractModelTest):
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    def get_default_attributes(self) -> Dict[str, Any]:
        return {
            "_name": "mockvariant",
            "_problem_factories": [
                self.build_problem_base,
                self.build_problem_no_speed,
            ],
            "_domain": self.domain(),
            "_problems": dict(),
        }

    def get_abstract_instance(self) -> Any:
        return AbstractVariant()

    def get_instance(self) -> Any:
        return MockvariantVariant(
            self.domain(),
            [self.build_problem_base, self.build_problem_no_speed],
        )

    def build_problem_base(self, problem: Problem):
        if int(problem.uid) > 0:
            return MagicMock()
        return None

    def build_problem_no_speed(self, problem: Problem):
        if int(problem.uid) > 0:
            return MagicMock()
        return None

    def domain(self):
        if not hasattr(self, "_domain"):
            self._domain = MagicMock()
        return self._domain

    @pytest.fixture()
    def variant(self, request):
        variant = self.get_instance()

        def teardown():
            variant._problems.clear()

        request.addfinalizer(teardown)
        yield variant

    @pytest.fixture()
    def tracked_variant(self):
        yield TrackedvariantVariant(
            self.domain(),
            [self.build_problem_base, self.build_problem_no_speed],
        )

    @staticmethod
    @pytest.fixture()
    def problem(request):
        problem_patch = patch("tyr.problem.model.problem.Problem")
        problem = problem_patch.start()
        problem.uid = "05"
        problem.is_empty = False
        request.addfinalizer(problem_patch.stop)
        yield problem

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    # =============================== Build problem ============================== #

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_build_problem_version_names(
        self,
        variant: AbstractVariant,
        problem_id: str,
    ):
        problem = variant.build_problem(problem_id)
        assert list(problem.versions.keys()) == ["base", "no_speed"]

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_build_problem_version_values(
        self,
        variant: AbstractVariant,
        problem_id: str,
    ):
        problem = variant.build_problem(problem_id)
        if problem_id == "-02":
            for version in problem.versions.values():
                assert version.value is None
        else:
            for version in problem.versions.values():
                assert isinstance(version.value, MagicMock)

    # =============================== Save to cache ============================== #

    @pytest.mark.parametrize("problem_id", ["01", "05", "13"])
    def test_save_problem_to_empty_cache(
        self,
        variant: AbstractVariant,
        problem: Problem,
        problem_id: str,
    ):
        problem.uid = problem_id
        assert variant._problems == dict()
        variant.save_problem_to_cache(problem)
        assert variant._problems == {problem_id: problem}
        variant.save_problem_to_cache(problem)
        assert variant._problems == {problem_id: problem}

    def test_save_problem_to_non_empty_cache(
        self,
        variant: AbstractVariant,
        problem: Problem,
    ):
        base_problem = MagicMock()
        variant._problems = {"213": base_problem}
        variant.save_problem_to_cache(problem)
        assert variant._problems == {"213": base_problem, "05": problem}

    def test_save_null_problem_to_cache(self, variant: AbstractVariant):
        variant.save_problem_to_cache(None)
        assert variant._problems == dict()

    # ============================== Load from cache ============================= #

    def test_get_present_problem_from_cache(
        self,
        variant: AbstractVariant,
        problem: Problem,
    ):
        variant.save_problem_to_cache(problem)
        result = variant.get_problem_from_cache(problem.uid)
        assert result == problem

    def test_get_absent_problem_from_cache(self, variant: AbstractVariant):
        result = variant.get_problem_from_cache("01")
        assert result is None

    # ================================ Get problem =============================== #

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_get_problem_load_from_cache(
        self,
        tracked_variant: TrackedvariantVariant,
        problem_id: str,
    ):
        tracked_variant._problems = {"01": MagicMock()}
        tracked_variant.get_problem(problem_id)
        assert tracked_variant.from_cache_count == 1

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_get_problem_save_to_cache(
        self,
        tracked_variant: TrackedvariantVariant,
        problem_id: str,
    ):
        problem = MagicMock()
        problem.is_empty = False
        tracked_variant._problems = {"01": problem}
        tracked_variant.get_problem(problem_id)
        assert tracked_variant.save_cache_count == 1

    def test_get_present_problem(
        self,
        tracked_variant: TrackedvariantVariant,
        problem: Problem,
    ):
        tracked_variant.save_problem_to_cache(problem)
        result = tracked_variant.get_problem(problem.uid)
        assert result == problem
        assert tracked_variant.build_count == 0

    def test_get_absent_problem(
        self,
        tracked_variant: TrackedvariantVariant,
        problem: Problem,
    ):
        result = tracked_variant.get_problem(problem.uid)
        assert result is not None
        assert tracked_variant.build_count == 1

    def test_get_inexistant_problem(self, tracked_variant: TrackedvariantVariant):
        result = tracked_variant.get_problem("-02")
        assert result is not None  # Not None but generated problems are None
        assert tracked_variant.build_count == 1

    @pytest.mark.parametrize("problem_id", ["01", "05", "-02"])
    def test_get_problem_versions_are_lazy(
        self,
        variant: AbstractVariant,
        problem_id: str,
    ):
        result = variant.get_problem(problem_id)
        assert all(isinstance(v, Lazy) for v in result.versions.values())

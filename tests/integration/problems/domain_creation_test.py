import pytest
from unified_planning.shortcuts import AbstractProblem

from tests.integration.problems.domains import FakeDomain
from tyr import AbstractDomain, get_all_domains

REAL_FAILED = [
    "ipc1998-logistics-round1-adl",
    "ipc1998-mystery-prime-round1-adl",
    "ipc1998-mystery-round1-adl",
    "ipc2000-freecell-strips-typed",
    "ipc2000-logistics-strips-untyped",
    "ipc2000-schedule-adl-typed",
    "ipc2002-driverlog-numeric-automatic",
    "ipc2002-driverlog-numeric-hand-coded",
    "ipc2002-driverlog-numeric-hard-automatic",
    "ipc2002-driverlog-numeric-hard-hand-coded",
    "ipc2002-rovers-time-automatic",
    "ipc2002-rovers-time-hand-coded",
    "ipc2002-settlers-numeric-automatic",
    "ipc2002-zenotravel-numeric-automatic",
    "ipc2002-zenotravel-numeric-hand-coded",
    "ipc2002-zenotravel-strips-automatic",
    "ipc2002-zenotravel-strips-hand-coded",
    "ipc2002-zenotravel-time-automatic",
    "ipc2002-zenotravel-time-hand-coded",
    "ipc2002-zenotravel-time-simple-automatic",
    "ipc2002-zenotravel-time-simple-hand-coded",
    "ipc2004-pipesworld-no-tankage-temporal-deadlines-compiled-strips",
    "ipc2004-promela-dining-philosophers-adl",
    "ipc2004-promela-dining-philosophers-derived-predicates-adl",
    "ipc2004-promela-dining-philosophers-derived-predicates-strips",
    "ipc2004-promela-dining-philosophers-fluents-adl",
    "ipc2004-promela-dining-philosophers-fluents-derived-predicates-adl",
    "ipc2004-promela-optical-telegraph-adl",
    "ipc2004-promela-optical-telegraph-derived-predicates-adl",
    "ipc2004-promela-optical-telegraph-derived-predicates-strips",
    "ipc2004-promela-optical-telegraph-fluents-adl",
    "ipc2004-promela-optical-telegraph-fluents-derived-predicates-adl",
    "ipc2004-psr-large-derived-predicates-adl",
    "ipc2004-psr-middle-compiled-adl",
    "ipc2004-psr-middle-derived-predicates-adl",
    "ipc2004-psr-middle-derived-predicates-simple-adl",
    "ipc2004-psr-middle-derived-predicates-strips",
    "ipc2004-satellite-complex-time-windows-compiled-strips",
    "ipc2004-satellite-complex-time-windows-strips",
    "ipc2004-satellite-time-time-windows-compiled-strips",
    "ipc2006-openstacks-metric-time",
    "ipc2006-openstacks-metric-time-strips",
    "ipc2006-openstacks-preferences-qualitative",
    "ipc2006-openstacks-preferences-simple",
    "ipc2006-pathways-metric-time",
    "ipc2006-pathways-preferences-complex",
    "ipc2006-pathways-preferences-simple",
    "ipc2006-pathways-propositional",
    "ipc2006-pipesworld-metric-time-constraints",
    "ipc2006-pipesworld-preferences-complex",
    "ipc2006-rovers-metric-preferences-simple",
    "ipc2006-rovers-metric-time",
    "ipc2006-rovers-preferences-qualitative",
    "ipc2006-storage-preferences-complex",
    "ipc2006-storage-preferences-qualitative",
    "ipc2006-storage-preferences-simple",
    "ipc2006-storage-preferences-simple-grounded-preferences",
    "ipc2006-storage-propositional",
    "ipc2006-storage-time",
    "ipc2006-storage-time-constraints",
    "ipc2006-tpp-metric-time",
    "ipc2006-tpp-metric-time-constraints",
    "ipc2006-tpp-preferences-complex",
    "ipc2006-tpp-preferences-qualitative",
    "ipc2006-tpp-preferences-simple",
    "ipc2006-tpp-preferences-simple-grounded-preferences",
    "ipc2006-trucks-preferences-complex",
    "ipc2006-trucks-preferences-qualitative",
    "ipc2006-trucks-preferences-simple",
    "ipc2006-trucks-preferences-simple-grounded",
    "ipc2006-trucks-preferences-simple-grounded-preferences",
    "ipc2006-trucks-time-constraints",
    "ipc2008-crew-planning-net-benefit-optimal-numeric-fluents",
    "ipc2008-elevator-net-benefit-optimal-numeric-fluents",
    "ipc2008-elevator-net-benefit-optimal-strips",
    "ipc2008-model-train-temporal-satisficing-numeric-fluents",
    "ipc2008-openstacks-net-benefit-optimal-adl",
    "ipc2008-openstacks-net-benefit-optimal-adl-numeric-fluents",
    "ipc2008-openstacks-net-benefit-optimal-strips-negative-preconditions",
    "ipc2008-peg-solitaire-net-benefit-optimal-strips",
    "ipc2008-transport-net-benefit-optimal-numeric-fluents",
    "ipc2008-woodworking-net-benefit-optimal-numeric-fluents",
    "ipc2011-floor-tile-sequential-multi-core",
    "ipc2011-floor-tile-sequential-optimal",
    "ipc2011-floor-tile-sequential-satisficing",
    "ipc2011-floor-tile-temporal-satisficing",
    "ipc2011-storage-temporal-satisficing",
    "ipc2011-temporal-machine-shop-temporal-satisficing",
    "ipc2011-tidybot-sequential-multi-core",
    "ipc2011-tidybot-sequential-optimal",
    "ipc2011-tidybot-sequential-satisficing",
    "ipc2011-turn-and-open-temporal-satisficing",
    "ipc2014-floor-tile-sequential-agile",
    "ipc2014-floor-tile-sequential-multi-core",
    "ipc2014-floor-tile-sequential-optimal",
    "ipc2014-floor-tile-sequential-satisficing",
    "ipc2014-floor-tile-temporal-satisficing",
    "ipc2014-storage-temporal-satisficing",
    "ipc2014-temporal-machine-shop-temporal-satisficing",
    "ipc2014-tidybot-sequential-optimal",
    "ipc2014-turn-and-open-temporal-satisficing",
    "ipc2018-spider-sequential-optimal",
    "ipc2018-spider-sequential-satisficing",
    "ipc2020-barman-bdi-partial-order",
    "ipc2020-barman-bdi-total-order",
    "ipc2020-freecell-learned-ecai16-total-order",
    "ipc2020-um-translog-partial-order",
    "ipc2020-woodworking-partial-order",
    "ipc2023-markettrader-numeric",
    "ipc2023-sugar-numeric",
]

REAL_SKIPPED = ["ipc2008-cyber-security-sequential-satisficing-strips"]


class TestDomainCreation:
    @pytest.mark.parametrize(
        ["problem_id", "is_none"],
        [(i, not (0 < i <= 3)) for i in range(15)],
    )
    @pytest.mark.parametrize("version_name", ["a_first", "base", "modified"])
    def test_fake_domain_problem_creation(
        self,
        problem_id: int,
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
        ["domain", "problem_id", "version_name"],
        [
            (d, p, v)
            for d in get_all_domains()
            for v in d.get_versions()
            # Test 1000 in order to check behaviour on non existant problem
            for p in [1, 1000]
        ],
        ids=lambda x: x if isinstance(x, (int, str)) else x.name,
    )
    def test_real_domain_creation(
        self,
        domain: AbstractDomain,
        problem_id: int,
        version_name: str,
    ):
        if domain.name in REAL_SKIPPED:
            pytest.skip("This domain is too long to be parsed")

        should_fail = (
            domain.name in REAL_FAILED and problem_id != 1000 and version_name == "base"
        )
        problem = domain.get_problem(problem_id)
        assert problem is not None, "The domain is empty, consider to remove it."
        version = problem.versions[version_name]

        try:
            version.value  # Check the value can be accessed without error.
            if should_fail:
                pytest.fail("This domain should fail")
        except Exception as e:
            if should_fail:
                pytest.xfail(str(e))
            else:
                raise e from e

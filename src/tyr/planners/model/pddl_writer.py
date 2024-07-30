import sys
from typing import IO, List, cast

from unified_planning.exceptions import (
    UPProblemDefinitionError,
    UPTypeError,
    UPUnsupportedProblemTypeError,
)
from unified_planning.io.pddl_writer import (
    ConverterToPDDLString,
    ObjectsExtractor,
    PDDLWriter,
    _get_pddl_name,
    _update_domain_objects,
    _write_effect,
)
from unified_planning.model import (
    DurativeAction,
    InstantaneousAction,
    MinimizeActionCosts,
    StartTiming,
    Type,
)
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.model.types import _UserType


class TyrPDDLWriter(PDDLWriter):
    # pylint: disable=arguments-renamed

    """This class is a copy of the original PDDLWriter with some changes.

    Changes:
        - Support of control parameters.
    """

    def print_domain(
        self,
        /,
        control_support: bool = False,
        all_support: bool = False,
    ):
        """Prints to std output the `PDDL` domain.

        Args:
            control_support (bool): If True, the domain will be printed with control parameters.
            all_support (bool): If True, the domain will be printed with supported changes.
        """
        self._write_domain(sys.stdout, control_support, all_support)

    def write_domain(
        self,
        filename: str,
        /,
        control_support: bool = False,
        all_support: bool = False,
    ):
        """Dumps to file the `PDDL` domain.

        Args:
            control_support (bool): If True, the domain will be printed with control parameters.
            all_support (bool): If True, the domain will be printed with supported changes."""
        with open(filename, "w", encoding="utf-8") as f:
            self._write_domain(f, control_support, all_support)

    def _write_domain(
        self,
        out: IO[str],
        control_support: bool = False,
        all_support: bool = False,
    ):
        # pylint: disable=too-many-branches, too-many-statements, too-many-locals, line-too-long, too-many-nested-blocks # noqa: E501
        if self.problem_kind.has_intermediate_conditions_and_effects():
            raise UPProblemDefinitionError(
                "PDDL does not support ICE.\nICE are Intermediate Conditions and Effects therefore when an Effect (or Condition) are not at StartTIming(0) or EndTIming(0)."  # noqa: E501
            )
        if self.problem_kind.has_timed_goals():
            raise UPProblemDefinitionError("PDDL does not support timed goals.")
        obe = ObjectsExtractor()
        out.write("(define ")
        if self.problem.name is None:
            name = "pddl"
        else:
            name = _get_pddl_name(self.problem)
        out.write(f"(domain {name}-domain)\n")

        if self.needs_requirements:
            out.write(" (:requirements :strips")
            if self.problem_kind.has_flat_typing():
                out.write(" :typing")
            if self.problem_kind.has_negative_conditions():
                out.write(" :negative-preconditions")
            if self.problem_kind.has_disjunctive_conditions():
                out.write(" :disjunctive-preconditions")
            if self.problem_kind.has_equalities():
                out.write(" :equality")
            if (
                self.problem_kind.has_int_fluents()
                or self.problem_kind.has_real_fluents()
                or self.problem_kind.has_fluents_in_actions_cost()
            ):
                out.write(" :numeric-fluents")
            if self.problem_kind.has_conditional_effects():
                out.write(" :conditional-effects")
            if self.problem_kind.has_existential_conditions():
                out.write(" :existential-preconditions")
            if (
                self.problem_kind.has_trajectory_constraints()
                or self.problem_kind.has_state_invariants()
            ):
                out.write(" :constraints")
            if self.problem_kind.has_universal_conditions():
                out.write(" :universal-preconditions")
            if (
                self.problem_kind.has_continuous_time()
                or self.problem_kind.has_discrete_time()
            ):
                out.write(" :durative-actions")
            if self.problem_kind.has_duration_inequalities():
                out.write(" :duration-inequalities")
            if (
                self.problem_kind.has_actions_cost()
                or self.problem_kind.has_plan_length()
            ):
                out.write(" :action-costs")
            if self.problem_kind.has_timed_effects():
                only_bool = True
                for le in self.problem.timed_effects.values():
                    for e in le:
                        if not e.fluent.type.is_bool_type():
                            only_bool = False
                if not only_bool:
                    out.write(" :timed-initial-effects")
                else:
                    out.write(" :timed-initial-literals")
            if self.problem_kind.has_hierarchical():
                out.write(" :hierarchy")  # HTN / HDDL
            if self.problem_kind.has_method_preconditions():
                out.write(" :method-preconditions")
            out.write(")\n")

        if self.problem_kind.has_hierarchical_typing():
            user_types_hierarchy = self.problem.user_types_hierarchy
            out.write(" (:types\n")
            stack: List[Type] = (
                user_types_hierarchy[None] if None in user_types_hierarchy else []
            )
            out.write(
                f'    {" ".join(self._get_mangled_name(t) for t in stack)} - object\n'
            )
            while stack:
                current_type = stack.pop()
                direct_sons: List[Type] = user_types_hierarchy[current_type]
                if direct_sons:
                    stack.extend(direct_sons)
                    out.write(
                        f'    {" ".join([self._get_mangled_name(t) for t in direct_sons])} - {self._get_mangled_name(current_type)}\n'  # noqa: E501
                    )
            out.write(" )\n")
        else:
            pddl_types = [
                self._get_mangled_name(t)
                for t in self.problem.user_types
                if cast(_UserType, t).name != "object"
            ]
            out.write(
                f' (:types {" ".join(pddl_types)})\n' if len(pddl_types) > 0 else ""
            )

        if self.domain_objects is None:
            # This method populates the self._domain_objects map
            self._populate_domain_objects(obe)
        assert self.domain_objects is not None  # nosec: B101

        if len(self.domain_objects) > 0:
            out.write(" (:constants")
            for ut, os in self.domain_objects.items():
                if len(os) > 0:
                    out.write(
                        f'\n   {" ".join([self._get_mangled_name(o) for o in os])} - {self._get_mangled_name(ut)}'  # noqa: E501
                    )
            out.write("\n )\n")

        predicates = []
        functions = []
        for f in self.problem.fluents:
            if f.type.is_bool_type():
                params = []
                i = 0
                for param in f.signature:
                    if param.type.is_user_type():
                        params.append(
                            f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"  # noqa: E501
                        )
                        i += 1
                    else:
                        raise UPTypeError("PDDL supports only user type parameters")
                predicates.append(f'({self._get_mangled_name(f)}{"".join(params)})')
            elif f.type.is_int_type() or f.type.is_real_type():
                params = []
                i = 0
                for param in f.signature:
                    if param.type.is_user_type():
                        params.append(
                            f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"  # noqa: E501
                        )
                        i += 1
                    else:
                        raise UPTypeError("PDDL supports only user type parameters")
                functions.append(f'({self._get_mangled_name(f)}{"".join(params)})')
            else:
                raise UPTypeError("PDDL supports only boolean and numerical fluents")
        if self.problem.kind.has_actions_cost() or self.problem.kind.has_plan_length():
            functions.append("(total-cost)")
        out.write(
            f' (:predicates {" ".join(predicates)})\n' if len(predicates) > 0 else ""
        )
        out.write(
            f' (:functions {" ".join(functions)})\n' if len(functions) > 0 else ""
        )

        converter = ConverterToPDDLString(
            self.problem.environment, self._get_mangled_name
        )
        costs = {}
        metrics = self.problem.quality_metrics
        if len(metrics) == 1:
            metric = metrics[0]
            if isinstance(metric, MinimizeActionCosts):
                for a in self.problem.actions:
                    cost_exp = metric.get_action_cost(a)
                    costs[a] = cost_exp
                    if cost_exp is not None:
                        _update_domain_objects(self.domain_objects, obe.get(cost_exp))
            elif metric.is_minimize_sequential_plan_length():
                for a in self.problem.actions:
                    costs[a] = self.problem.environment.expression_manager.Int(1)
        elif len(metrics) > 1:
            raise UPUnsupportedProblemTypeError("Only one metric is supported!")
        em = self.problem.environment.expression_manager
        if isinstance(self.problem, HierarchicalProblem):
            for task in self.problem.tasks:
                out.write(f" (:task {self._get_mangled_name(task)}")
                out.write("\n  :parameters (")
                for ap in task.parameters:
                    if ap.type.is_user_type():
                        out.write(
                            f" {self._get_mangled_name(ap)} - {self._get_mangled_name(ap.type)}"
                        )
                    else:
                        raise UPTypeError("PDDL supports only user type parameters")
                out.write("))\n")

            for m in self.problem.methods:
                out.write(f" (:method {self._get_mangled_name(m)}")
                out.write("\n  :parameters (")
                for ap in m.parameters:
                    if ap.type.is_user_type():
                        out.write(
                            f" {self._get_mangled_name(ap)} - {self._get_mangled_name(ap.type)}"
                        )
                    else:
                        raise UPTypeError("PDDL supports only user type parameters")
                out.write(")")

                params_str = " ".join(
                    converter.convert(em.ParameterExp(p))
                    for p in m.achieved_task.parameters
                )
                out.write(
                    f"\n  :task ({self._get_mangled_name(m.achieved_task.task)} {params_str})"
                )
                if len(m.preconditions) > 0:
                    precond_str: List[str] = []
                    for p in (c.simplify() for c in m.preconditions):
                        if not p.is_true():
                            if p.is_and():
                                precond_str.extend(map(converter.convert, p.args))
                            else:
                                precond_str.append(converter.convert(p))
                    out.write(f'\n  :precondition (and {" ".join(precond_str)})')
                elif len(m.preconditions) == 0 and self.empty_preconditions:
                    out.write("\n  :precondition ()")
                self._write_task_network(m, out, converter)
                out.write(")\n")

        for oa in self.problem.actions:
            a = oa.clone()
            if isinstance(a, InstantaneousAction):
                if any(p.simplify().is_false() for p in a.preconditions):
                    continue
                out.write(f" (:action {self._get_mangled_name(a)}")
                out.write("\n  :parameters (")
                controls = []
                for ap in a.parameters:
                    if ap.type.is_user_type():
                        out.write(
                            f" {self._get_mangled_name(ap)} - {self._get_mangled_name(ap.type)}"
                        )
                    elif control_support or all_support:
                        if (
                            ap.type.is_bool_type()
                            or ap.type.is_int_type()
                            or ap.type.is_real_type()
                        ):
                            controls.append(ap)
                        else:
                            raise UPTypeError(
                                "PDDL supports only user/bool/int/real type parameters"
                            )
                    else:
                        raise UPTypeError("PDDL supports only user type parameters")
                out.write(")")
                if len(controls) > 0:
                    out.write("\n  :control (")
                    for ap in controls:
                        if ap.type.is_bool_type():
                            out.write(f" {self._get_mangled_name(ap)} - bool")
                        elif ap.type.is_int_type():
                            out.write(f" {self._get_mangled_name(ap)} - integer")
                            if ap.type.lower_bound is not None:
                                a.add_precondition(em.GE(ap, ap.type.lower_bound))
                            if ap.type.upper_bound is not None:
                                a.add_precondition(em.LE(ap, ap.type.upper_bound))
                        elif ap.type.is_real_type():
                            out.write(f" {self._get_mangled_name(ap)} - number")
                            if ap.type.lower_bound is not None:
                                a.add_precondition(em.GE(ap, ap.type.lower_bound))
                            if ap.type.upper_bound is not None:
                                a.add_precondition(em.LE(ap, ap.type.upper_bound))
                        else:
                            raise UPTypeError(
                                "Control Parameters supports only bool/int/real type parameters"
                            )
                    out.write(")")
                if len(a.preconditions) > 0:
                    precond_str = []
                    for p in (c.simplify() for c in a.preconditions):
                        if not p.is_true():
                            if p.is_and():
                                precond_str.extend(map(converter.convert, p.args))
                            else:
                                precond_str.append(converter.convert(p))
                    out.write(f'\n  :precondition (and {" ".join(precond_str)})')
                elif len(a.preconditions) == 0 and self.empty_preconditions:
                    out.write("\n  :precondition ()")
                if len(a.effects) > 0:
                    out.write("\n  :effect (and")
                    for e in a.effects:
                        _write_effect(
                            e,
                            None,
                            out,
                            converter,
                            self.rewrite_bool_assignments,
                            self._get_mangled_name,
                        )

                    if oa in costs:
                        out.write(
                            f" (increase (total-cost) {converter.convert(costs[oa])})"
                        )
                    out.write(")")
                out.write(")\n")
            elif isinstance(a, DurativeAction):
                if any(
                    c.simplify().is_false() for cl in a.conditions.values() for c in cl
                ):
                    continue
                out.write(f" (:durative-action {self._get_mangled_name(a)}")
                out.write("\n  :parameters (")
                controls = []
                for ap in a.parameters:
                    if ap.type.is_user_type():
                        out.write(
                            f" {self._get_mangled_name(ap)} - {self._get_mangled_name(ap.type)}"
                        )
                    elif control_support or all_support:
                        if (
                            ap.type.is_bool_type()
                            or ap.type.is_int_type()
                            or ap.type.is_real_type()
                        ):
                            controls.append(ap)
                        else:
                            raise UPTypeError(
                                "PDDL supports only user/bool/int/real type parameters"
                            )
                    else:
                        raise UPTypeError("PDDL supports only user type parameters")
                out.write(")")
                if len(controls) > 0:
                    out.write("\n  :control (")
                    for ap in controls:
                        if ap.type.is_bool_type():
                            out.write(f" {self._get_mangled_name(ap)} - bool")
                        elif ap.type.is_int_type():
                            out.write(f" {self._get_mangled_name(ap)} - integer")
                            if ap.type.lower_bound is not None:
                                a.add_condition(
                                    StartTiming(), em.GE(ap, ap.type.lower_bound)
                                )
                            if ap.type.upper_bound is not None:
                                a.add_condition(
                                    StartTiming(), em.LE(ap, ap.type.upper_bound)
                                )
                        elif ap.type.is_real_type():
                            out.write(f" {self._get_mangled_name(ap)} - number")
                            if ap.type.lower_bound is not None:
                                a.add_condition(
                                    StartTiming(), em.GE(ap, ap.type.lower_bound)
                                )
                            if ap.type.upper_bound is not None:
                                a.add_condition(
                                    StartTiming(), em.LE(ap, ap.type.upper_bound)
                                )
                        else:
                            raise UPTypeError(
                                "Control Parameters supports only bool/int/real type parameters"
                            )
                    out.write(")")
                l, r = a.duration.lower, a.duration.upper
                if l == r:
                    out.write(f"\n  :duration (= ?duration {converter.convert(l)})")
                else:
                    out.write("\n  :duration (and ")
                    if a.duration.is_left_open():
                        out.write(f"(> ?duration {converter.convert(l)})")
                    else:
                        out.write(f"(>= ?duration {converter.convert(l)})")
                    if a.duration.is_right_open():
                        out.write(f"(< ?duration {converter.convert(r)})")
                    else:
                        out.write(f"(<= ?duration {converter.convert(r)})")
                    out.write(")")
                if len(a.conditions) > 0:
                    out.write("\n  :condition (and ")
                    for interval, cl in a.conditions.items():
                        for c in (cond.simplify() for cond in cl):
                            if c.is_true():
                                continue
                            if interval.lower == interval.upper:
                                if interval.lower.is_from_start():
                                    out.write(f"(at start {converter.convert(c)})")
                                else:
                                    out.write(f"(at end {converter.convert(c)})")
                            else:
                                if not interval.is_left_open():
                                    out.write(f"(at start {converter.convert(c)})")
                                out.write(f"(over all {converter.convert(c)})")
                                if not interval.is_right_open():
                                    out.write(f"(at end {converter.convert(c)})")
                    out.write(")")
                elif len(a.conditions) == 0 and self.empty_preconditions:
                    out.write("\n  :condition (and )")
                if len(a.effects) > 0:
                    out.write("\n  :effect (and")
                    for t, el in a.effects.items():
                        for e in el:
                            _write_effect(
                                e,
                                t,
                                out,
                                converter,
                                self.rewrite_bool_assignments,
                                self._get_mangled_name,
                            )
                    if oa in costs:
                        out.write(
                            f" (at end (increase (total-cost) {converter.convert(costs[oa])}))"
                        )
                    out.write(")")
                out.write(")\n")
            else:
                raise NotImplementedError
        out.write(")\n")

from typing import Callable, Generator

from bgpsecsim.asys import Relation, Route, RoutingPolicy

aspa_evaluation = []


class DefaultPolicy(RoutingPolicy):
    def accept_route(self, route: Route) -> bool:
        # not in combination with return, inverts the value
        return not route.contains_cycle()
        # If Route contains a cycle, then it returns true -> the not inverts the bool and so the Route is declined as there is a cycel in it

    def prefer_route(self, current: Route, new: Route) -> bool:
        # assert triggers error as soon as condition is false, in this case, if both final AS aren't the same
        assert current.final == new.final, "routes must have same final AS"

        for rule in self.preference_rules():
            current_val = rule(current)
            new_val = rule(new)
            if current_val < new_val:
                return False
            if new_val < current_val:
                return True

        return False

    def forward_to(self, route: Route, relation: Relation) -> bool:
        asys = route.final
        first_hop_rel = asys.get_relation(route.first_hop)
        assert first_hop_rel is not None

        return first_hop_rel == Relation.CUSTOMER or relation == Relation.CUSTOMER

    # Generators are iterators, a kind of iterable you can only iterate over once. Generators do not store all the values in memory, they generate the values on the fly:
    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # 1. Local preferences
        def local_pref(route):
            relation = route.final.get_relation(route.first_hop)
            return relation.value if relation else -1
        yield local_pref
        # 2. AS-path length
        yield lambda route: route.length
        # 3. Next hop AS number
        yield lambda route: route.first_hop.as_id


class RPKIPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        return super().accept_route(route) and not route.origin_invalid


class PathEndValidationPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        return super().accept_route(route) and not route.path_end_invalid


class BGPsecHighSecPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        # Rule should actually be to reject unauthenticated routes if all ASs on it have
        # bgp_sec_enabled, but that is less convenient in our simulation.
        return super().accept_route(route) and not route.origin_invalid

    # Lambda takes several arguments, but only has one expression
    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # Prefer authenticated routes
        yield lambda route: not route.authenticated

        # 1. Local preferences
        def local_pref(route):
            relation = route.final.get_relation(route.first_hop)
            return relation.value if relation else -1
        yield local_pref
        # 2. AS-path length
        yield lambda route: route.length
        # 3. Next hop AS number
        yield lambda route: route.first_hop.as_id


class BGPsecMedSecPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        # Rule should actually be to reject unauthenticated routes if all ASs on it have
        # bgp_sec_enabled, but that is less convenient in our simulation.
        return super().accept_route(route) and not route.origin_invalid

    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # 1. Local preferences
        def local_pref(route):
            relation = route.final.get_relation(route.first_hop)
            return relation.value if relation else -1
        yield local_pref
        # Prefer authenticated routes
        yield lambda route: not route.authenticated
        # 2. AS-path length
        yield lambda route: route.length
        # 3. Next hop AS number
        yield lambda route: route.first_hop.as_id


class BGPsecLowSecPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        # Rule should actually be to reject unauthenticated routes if all ASs on it have
        # bgp_sec_enabled, but that is less convenient in our simulation.
        return super().accept_route(route) and not route.origin_invalid

    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # 1. Local preferences
        def local_pref(route):
            relation = route.final.get_relation(route.first_hop)
            return relation.value if relation else -1
        yield local_pref
        # 2. AS-path length
        yield lambda route: route.length
        # Prefer authenticated routes
        yield lambda route: not route.authenticated
        # 3. Next hop AS number
        yield lambda route: route.first_hop.as_id


def test_route_aspa(route: Route) -> None:
    aspa_evaluation.clear()
    for index, r in enumerate(route.path):
        if index + 1 < len(route.path) and index - 1 >= 0:
            prev_el = route.path[index - 1]
            curr_el = r
            next_el = route.path[index + 1]
        else:
            break
        # TODO ASPA muss bereits vorher erstellt werden, da sonst alle AS der Route ein ASPA haben, auch die AS der malicious Route; Alternativ muss das Flag nur bei den korrekten gesetzt werden
        r.create_new_aspa()
        # If an ASPA Flag is not set, so AS has no ASPA Object, empty aspa_evaluation is returned,
        # thus contains no INVALID and route is accepted at the end
        if curr_el.aspa_enabled:
            a = curr_el.get_aspa_providers()
            if len(a) == 0:
                aspa_evaluation.append("UNKNOWN")
            else:
                # If ASPA Object is not empty and next / before AS is contained in the corresponding ASes
                # ASPA Object will return VALID otherwise invalid will be returned
                for elements in a:
                    if next_el == elements:
                        aspa_evaluation.append("VALID")
                        break
                for elements in a:
                    if prev_el == elements:
                        aspa_evaluation.append("VALID")
                        break
                aspa_evaluation.append("INVALID")
                break


class ASPAPolicy(DefaultPolicy):

    def accept_route(self, route: Route) -> bool:
        test_route_aspa(route)
        # Accepts the route of none of the elements with ASPA activated has returned INVALID
        return super().accept_route(route) and not ("INVALID" in aspa_evaluation)

    # Lambda takes several arguments, but only has one expression
    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # TODO Wird hier die Route richtig übergeben??
        yield lambda route: test_route_aspa(route)
        # Prefer fully VALID
        yield lambda route: not ("INVALID" and "UNKNOWN" in aspa_evaluation)
        # Prefer VALID and UNKNOWN; discard all INVALID
        yield lambda route: not ("INVALID" in aspa_evaluation)

        # 1. Local preferences
        def local_pref(route):
            relation = route.final.get_relation(route.first_hop)
            return relation.value if relation else -1
        yield local_pref
        # 2. AS-path length
        yield lambda route: route.length
        # 3. Next hop AS number
        yield lambda route: route.first_hop.as_id

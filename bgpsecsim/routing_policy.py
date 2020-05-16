from typing import Callable, Generator, Optional

from bgpsecsim.asys import Relation, Route, RoutingPolicy

class DefaultPolicy(RoutingPolicy):
    def accept_route(self, route: Route) -> bool:
        return True

    def prefer_route(self, current: Route, new: Route) -> bool:
        assert current.origin == new.origin, "routes must have same origin AS"
        assert current.final == new.final, "routes must have same final AS"

        for rule in self.preference_rules():
            current_val = rule(current)
            new_val = rule(new)
            if current_val < new_val:
                return current
            if new_val < current_val:
                return new

        return current

    def forward_to(self, route: Route, relation: Relation) -> bool:
        asys = route.final
        first_hop_rel = asys.get_relation(route.first_hop)
        assert first_hop_rel is not None

        return first_hop_rel == Relation.CUSTOMER or relation == Relation.CUSTOMER

    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # 1. Local preferences
        yield lambda route: route.final.get_relation(route.first_hop),
        # 2. AS-path length
        yield lambda route: route.length,
        # 3. Next hop AS number
        yield lambda route: route.next_hop.as_id,

class RPKIPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        return not route.origin_invalid

class PathEndValidationPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        return not route.path_end_invalid

class BGPsecHighSecPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        return route.authenticated or (
            not route.next_hop.bgp_sec_enabled and not route.origin_invalid)

    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # Prefer authenticated routes
        yield lambda route: not route.authenticated
        # 1. Local preferences
        yield lambda route: route.final.get_relation(route.first_hop),
        # 2. AS-path length
        yield lambda route: route.length,
        # 3. Next hop AS number
        yield lambda route: route.next_hop.as_id,

class BGPsecMedSecPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        return route.authenticated or (
            not route.next_hop.bgp_sec_enabled and not route.origin_invalid)

    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # 1. Local preferences
        yield lambda route: route.final.get_relation(route.first_hop),
        # Prefer authenticated routes
        yield lambda route: not route.authenticated
        # 2. AS-path length
        yield lambda route: route.length,
        # 3. Next hop AS number
        yield lambda route: route.next_hop.as_id,

class BGPsecLowSecPolicy(DefaultPolicy):
    def accept_route(self, route: Route) -> bool:
        return route.authenticated or (
            not route.next_hop.bgp_sec_enabled and not route.origin_invalid)

    def preference_rules(self) -> Generator[Callable[[Route], int], None, None]:
        # 1. Local preferences
        yield lambda route: route.final.get_relation(route.first_hop),
        # 2. AS-path length
        yield lambda route: route.length,
        # Prefer authenticated routes
        yield lambda route: not route.authenticated
        # 3. Next hop AS number
        yield lambda route: route.next_hop.as_id,

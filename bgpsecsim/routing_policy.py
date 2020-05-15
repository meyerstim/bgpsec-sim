from typing import Optional

from asys import AS, Relation, Route

def local_preference(self, current: Route, new: Route) -> Optional[Route]:
    assert current.origin == new.origin, "routes must have same origin AS"
    assert current.final == new.final, "routes must have same final AS"

    asys = current.final
    current_first_hop_rel = asys.get_relation(current[-2])
    new_first_hop_rel = asys.get_relation(new[-2])

    if new_first_hop_rel < current_first_hop_rel:
       return new
    if current_first_hop_rel < new_first_hop_rel:
       return current
    return None

def prefer_by_path_length(self, current: Route, new: Route) -> Optional[Route]:
    assert current.origin == new.origin, "routes must have same origin AS"
    assert current.final == new.final, "routes must have same final AS"

    asys = current.final
    current_path_length = current.length
    new_path_length = new.length

    if current_path_length:

class RoutingPolicy(object):
    def accept_route(self, route: Route) -> bool:
        pass

    def prefer_route(self, current: Route, new: Route) -> bool:
        assert current.origin == new.origin, "routes must have same origin AS"
        assert current.final == new.final, "routes must have same final AS"

        rules = [
            # 1. Local preferences
            lambda route: route.final.get_relation(route.first_hop),
            # 2. AS-path length
            lambda route: route.length,
            # 3. Next hop AS number
            lambda route: route.next_hop.as_id,
        ]

        for rule in rules:
            current_val = rule(current)
            new_val = rule(new)
            if current_val < new_val:
                return current
            if new_val < current_val:
                return new

        return current

    def forward_to(self, route: Route, relation: Relation) -> bool:
        pass

    def preference_rules(self, current: Route, new: 

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

    def preference_rules(self):
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

    def preference_rules(self):
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

    def preference_rules(self):
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

    def preference_rules(self):
        # 1. Local preferences
        yield lambda route: route.final.get_relation(route.first_hop),
        # 2. AS-path length
        yield lambda route: route.length,
        # Prefer authenticated routes
        yield lambda route: not route.authenticated
        # 3. Next hop AS number
        yield lambda route: route.next_hop.as_id,

from enum import Enum
from typing import Dict, List, Optional

AS_ID = int

class Relation(Enum):
    CUSTOMER = 1
    PEER = 2
    PROVIDER = 3

class AS(object):
    __slots__ = [
        'as_id', 'neighbors', 'policy', 'publishes_rpki', 'publishes_path_end', 'bgp_sec_enabled',
        'routing_table'
    ]

    as_id: AS_ID
    neighbors: Dict['AS', Relation]
    policy: 'RoutingPolicy'
    publishes_rpki: bool
    publishes_path_end: bool
    bgp_sec_enabled: bool
    routing_table: Dict[AS_ID, 'Route']

    def __init__(
        self,
        as_id: AS_ID,
        policy: 'RoutingPolicy',
        publishes_rpki: bool = False,
        publishes_path_end: bool = False,
        bgp_sec_enabled: bool = False
    ):
        self.as_id = as_id
        self.policy = policy
        self.neighbors = {}
        self.publishes_rpki = publishes_rpki
        self.publishes_path_end = publishes_path_end
        self.bgp_sec_enabled = bgp_sec_enabled

        self_route = Route(
            [self],
            origin_invalid=False,
            path_end_invalid=False,
            authenticated=True,
        )
        self.routing_table = { as_id: self_route }

    def add_peer(self, asys: 'AS'):
        self.neighbors[asys] = Relation.PEER

    def add_customer(self, asys: 'AS'):
        self.neighbors[asys] = Relation.CUSTOMER

    def add_provider(self, asys: 'AS'):
        self.neighbors[asys] = Relation.PROVIDER

    def get_relation(self, asys: 'AS') -> Optional[Relation]:
        return self.neighbors.get(asys, None)

    def learn_route(self, route: 'Route') -> List['AS']:
        """Learn about a new route.

        Returns a list of ASs to advertise route to.
        """
        if route.origin == self:
            return []

        if not self.policy.accept_route(route):
            return []

        origin_id = route.origin.as_id
        if (origin_id in self.routing_table and
            not self.policy.prefer_route(self.routing_table[origin_id], route)):
            return []

        self.routing_table[origin_id] = route

        forward_to_relations = set((relation
                                    for relation in Relation
                                    if self.policy.forward_to(route, relation)))

        return [neighbor
                for neighbor, relation in self.neighbors.items()
                if relation in forward_to_relations]

    def originate_route(self, next_hop: 'AS') -> 'Route':
        return Route(
            path=[self, next_hop],
            origin_invalid=False,
            path_end_invalid=False,
            authenticated=self.bgp_sec_enabled,
        )

    def forward_route(self, route: 'Route', next_hop: 'AS') -> 'Route':
        return Route(
            path=route.path + [next_hop],
            origin_invalid=route.origin_invalid,
            path_end_invalid=route.path_end_invalid,
            authenticated=route.authenticated and next_hop.bgp_sec_enabled,
        )

    def clear_routing_table(self):
        self.routing_table.clear()

class Route(object):
    __slots__ = ['path', 'origin_invalid', 'path_end_invalid', 'authenticated']

    path: List[AS]
    # Whether the origin has no valid RPKI record and one is expected.
    origin_invalid: bool
    # Whether the first hop has no valid path-end record and one is expected.
    path_end_invalid: bool
    # Whether the path is authenticated with BGPsec.
    authenticated: bool

    def __init__(
        self,
        path: List[AS],
        origin_invalid: bool,
        path_end_invalid: bool,
        authenticated: bool,
    ):
        self.path = path
        self.origin_invalid = origin_invalid
        self.path_end_invalid = path_end_invalid
        self.authenticated = authenticated

    @property
    def length(self) -> int:
        return len(self.path)

    @property
    def origin(self) -> AS:
        return self.path[0]

    @property
    def first_hop(self) -> AS:
        return self.path[-2]

    @property
    def final(self) -> AS:
        return self.path[-1]

    def __str__(self) -> AS:
        return ','.join((str(asys.as_id) for asys in self.path))

    def __repr__(self) -> AS:
        s = str(self)
        flags = []
        if self.origin_invalid:
            flags.append('origin_invalid')
        if self.path_end_invalid:
            flags.append('path_end_invalid')
        if self.authenticated:
            flags.append('authenticated')
        if flags:
            s += " " + " ".join(flags)
        return s

class RoutingPolicy(object):
    def accept_route(self, route: Route) -> bool:
        pass

    def prefer_route(self, current: Route, new: Route) -> bool:
        pass

    def forward_to(self, route: Route, relation: Relation) -> bool:
        pass

from enum import Enum
from typing import Dict, List, Optional

from routing_policy import RoutingPolicy

AS_ID = int

class Relation(Enum):
    CUSTOMER = 1
    PEER = 2
    PROVIDER = 3

class AS(object):
    __slots__ = [
        'as_id', 'neighbors', 'publishes_rpki', 'publishes_path_end', 'bgp_sec_enabled',
        'routing_table'
    ]

    as_id: AS_ID
    neighbors: Dict[AS, Relation]
    publishes_rpki: bool
    publishes_path_end: bool
    bgp_sec_enabled: bool
    routing_table: Dict[AS_ID, Route]

    def __init__(
        self,
        as_id: AS_ID,
        publishes_rpki: bool = False,
        publishes_path_end: bool = False,
        bgp_sec_enabled: bool = False
    ):
        self.as_id = as_id
        self.neighbors = {}
        self.publishes_pki = publishes_rpki
        self.publishes_path_end = publishes_path_end
        self.bgp_sec_enabled = bgp_sec_enabled
        self.routing_table = {}

    def add_peer(self, asys: AS):
        self.neighbors[asys] = Relation.PEER

    def add_customer(self, asys: AS):
        self.neighbors[asys] = Relation.CUSTOMER

    def add_provider(self, asys: AS):
        self.neighbors[asys] = Relation.PROVIDER

    def get_relation(self, asys: AS) -> Optional[Relation]:
        return self.neigbors.get(asys, None)

    @property
    def neighbors(self) -> List[AS]:
        return self.peers + self.customers + self.providers

    def learn_route(self, route: Route) -> List[AS]:
        """Learn about a new route.

        Returns a list of ASs to advertise route to.
        """
        if not self.policy.accept_route(route):
            return []

        origin_id = route.origin.as_id
        if (origin_id in self.routing_table and
            not self.policy.prefer_route(self.routing_table[origin_id], route)):
            return []

        self.routing_table[origin_id] = route

        forward_to = []
        if self.policy.forward_to_peers(route):
            forward_to.extend(self.peers)
        if self.policy.forward_to_customers(route):
            forward_to.extend(self.customers)
        if self.policy.forward_to_providers(route):
            forward_to.extend(self.providers)
        return forward_to

    def originate_route(self, next_hop: AS) -> Route:
        return Route(
            path=[self, next_hop],
            origin_invalid=False,
            path_end_invalid=False,
            authenticated=self.bgp_sec_enabled,
        )

    def forward_route(self, route: Route, next_hop: AS) -> Route:
        return Route(
            path=route.path + [next_hop],
            origin_invalid=route.origin_invalid,
            path_end_invalid=route.path_end_invalid,
            authenticated=route.authenticated and next_hop.bgp_sec_enabled,
        )

    def clear_routing_table(self):
        self.routing_table.clear()

class Route(object):
    path: List[AS]
    # Whether the origin has no valid RPKI record and one is expected.
    origin_valid: bool
    # Whether the first hop has no valid path-end record and one is expected.
    path_end_invalid: bool
    # Whether the path is authenticated with BGPsec.
    authenticated: bool

    def __init__(
        self,
        path: List[AS],
        origin_invalid: bool
        path_end_invalid: bool,
        authenticated: bool,
    ):
        self.path = path
        self.origin_invalid = origin_invalid
        self.path_end_invalid = path_end_invalid
        self.authenticated = authenticated

    @property
    def length(self) -> int:
        return len(path)

    @property
    def origin(self) -> AS:
        return self.path[0]

    @property
    def first_hop(self) -> AS:
        return self.path[-2]

    @property
    def final(self) -> AS:
        return self.path[-1]

Route = List[AS_ID]

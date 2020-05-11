from typing import List, Set

AS_ID = int
Route = List[AS_ID]

class AS(object):
    as_id: AS_ID
    peers: Set[AS]
    customers: Set[AS]
    providers: Set[AS]
    publishes_rpki: bool
    publishes_path_end: bool

    def __init__(self, as_id: AS_ID):
        self.as_id = as_id
        self.peers = set()
        self.customers = set()
        self.providers = set()

    def add_peer(self, peer: AS):
        self.peers.add(peer)

    def add_customer(self, customer: AS):
        self.customers.add(customer)

    def add_provider(self, provider: AS):
        self.providers.add(provider)

    def learn_route(self, route: Route) -> List[AS]:
        """Learn about a new route.

        Returns a list of ASs to advertise route to.
        """
        pass

    def clear_routing_table(self):
        pass

class RoutingPolicy(object):
    def __init__(self):
        pass

    def accept_route(self, route: Route) -> bool:
        pass

    def forward_to_peer(self, route: Route) -> bool:
        pass

    def forward_to_customer(self, route: Route) -> bool:
        pass

    def forward_to_provider(self, route: Route) -> bool:
        pass


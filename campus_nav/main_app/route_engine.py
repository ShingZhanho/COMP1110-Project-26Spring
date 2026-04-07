from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from ..models import CampusMap, Edge, EdgeType, Node

# Exponents controlling how much the speed multiplier affects each edge type.
# Higher exponent = more affected by speed changes.
_SPEED_EXPONENTS: dict[EdgeType, float] = {
    EdgeType.FLAT: 1.0,
    EdgeType.STAIRS: 1.5,
    EdgeType.MINOR_STAIRS: 1.3,
    EdgeType.ESCALATOR: 0.3,
    EdgeType.LIFT: 0.0,  # lifts are not affected by walking speed
}

_INF = float("inf")
_LIFT_PREFERENCE_FACTOR = 0.5


@dataclass
class Preferences:
    avoid_stairs: bool = False
    avoid_escalators: bool = False
    prefer_lifts: bool = False
    accessible: bool = False


@dataclass
class RouteStep:
    from_node: Node
    to_node: Node
    edge: Edge
    adjusted_cost: float


@dataclass
class Route:
    steps: list[RouteStep]
    total_cost: float
    labels: list[str] = field(default_factory=list)

    @property
    def num_stops(self) -> int:
        if not self.steps:
            return 0
        return len(self.steps) + 1

    @property
    def has_stairs(self) -> bool:
        return any(s.edge.edge_type in (EdgeType.STAIRS, EdgeType.MINOR_STAIRS) for s in self.steps)

    @property
    def has_lift(self) -> bool:
        return any(s.edge.edge_type == EdgeType.LIFT for s in self.steps)

    @property
    def has_escalator(self) -> bool:
        return any(s.edge.edge_type == EdgeType.ESCALATOR for s in self.steps)

    @property
    def total_original_cost(self) -> int:
        return sum(s.edge.time_cost for s in self.steps)

    def edge_key(self) -> tuple:
        return tuple(
            (s.from_node.node_id, s.to_node.node_id, s.edge.edge_type, s.edge.time_cost)
            for s in self.steps
        )


def compute_adjusted_cost(edge: Edge, speed_multiplier: float) -> float:
    """Compute the time cost of an edge adjusted for walking speed only."""
    exponent = _SPEED_EXPONENTS[edge.edge_type]
    effective = speed_multiplier ** exponent
    return edge.time_cost / max(effective, 1e-9)


def _cost_fn_for_strategy(edge: Edge, speed_multiplier: float, preferences: Preferences) -> float:
    """Cost function used during pathfinding (includes avoidance penalties)."""
    etype = edge.edge_type
    if preferences.avoid_stairs and etype in (EdgeType.STAIRS, EdgeType.MINOR_STAIRS):
        return _INF
    if preferences.avoid_escalators and etype == EdgeType.ESCALATOR:
        return _INF

    cost = compute_adjusted_cost(edge, speed_multiplier)

    if preferences.prefer_lifts and etype == EdgeType.LIFT:
        cost *= _LIFT_PREFERENCE_FACTOR

    return cost


def _dijkstra(
    campus_map: CampusMap,
    start_id: str,
    end_id: str,
    cost_fn,
) -> list[RouteStep] | None:
    nodes = {n.node_id: n for n in campus_map.get_nodes()}
    if start_id not in nodes or end_id not in nodes:
        return None

    dist: dict[str, float] = {nid: _INF for nid in nodes}
    prev: dict[str, tuple[str, Edge] | None] = {nid: None for nid in nodes}
    dist[start_id] = 0.0
    pq: list[tuple[float, str]] = [(0.0, start_id)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == end_id:
            break
        for edge in nodes[u].get_edges():
            v = edge.get_other_node_of(nodes[u]).node_id
            c = cost_fn(edge)
            if c >= _INF:
                continue
            nd = d + c
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = (u, edge)
                heapq.heappush(pq, (nd, v))

    if dist[end_id] >= _INF:
        return None

    steps: list[RouteStep] = []
    cur = end_id
    while prev[cur] is not None:
        pid, edge = prev[cur]
        steps.append(RouteStep(nodes[pid], nodes[cur], edge, 0.0))
        cur = pid
    steps.reverse()
    return steps


def _find_route(
    campus_map: CampusMap,
    waypoint_ids: list[str],
    cost_fn,
    speed_multiplier: float,
) -> Route | None:
    all_steps: list[RouteStep] = []
    for i in range(len(waypoint_ids) - 1):
        seg = _dijkstra(campus_map, waypoint_ids[i], waypoint_ids[i + 1], cost_fn)
        if seg is None:
            return None
        all_steps.extend(seg)

    # Compute actual adjusted costs for display
    for step in all_steps:
        step.adjusted_cost = compute_adjusted_cost(step.edge, speed_multiplier)
    total = sum(s.adjusted_cost for s in all_steps)
    return Route(steps=all_steps, total_cost=total)


def find_candidate_routes(
    campus_map: CampusMap,
    waypoint_ids: list[str],
    preferences: Preferences,
    speed_multiplier: float,
) -> list[Route]:
    """Generate multiple candidate routes using different strategies."""
    strategies: list[Preferences] = [
        # 1. User preferences as-is
        preferences,
        # 2. Force no stairs
        Preferences(
            avoid_stairs=True,
            avoid_escalators=preferences.avoid_escalators,
            prefer_lifts=preferences.prefer_lifts,
        ),
        # 3. Force prefer lifts
        Preferences(
            avoid_stairs=preferences.avoid_stairs,
            avoid_escalators=preferences.avoid_escalators,
            prefer_lifts=True,
        ),
    ]

    routes: list[Route] = []
    seen: set[tuple] = set()

    for prefs in strategies:
        cost_fn = lambda e, p=prefs: _cost_fn_for_strategy(e, speed_multiplier, p)
        route = _find_route(campus_map, waypoint_ids, cost_fn, speed_multiplier)
        if route is None:
            continue
        key = route.edge_key()
        if key in seen:
            continue
        seen.add(key)
        routes.append(route)

    # Fewest-stops strategy: uniform edge cost (respecting avoidance)
    def uniform_fn(e):
        base = _cost_fn_for_strategy(e, speed_multiplier, preferences)
        return _INF if base >= _INF else 1.0

    route = _find_route(campus_map, waypoint_ids, uniform_fn, speed_multiplier)
    if route is not None:
        key = route.edge_key()
        if key not in seen:
            seen.add(key)
            routes.append(route)

    _assign_labels(routes)
    return routes


def _assign_labels(routes: list[Route]) -> None:
    if not routes:
        return
    min_cost = min(r.total_cost for r in routes)
    min_stops = min(len(r.steps) for r in routes)
    for route in routes:
        if abs(route.total_cost - min_cost) < 0.01:
            route.labels.append("Fastest")
        if len(route.steps) == min_stops:
            route.labels.append("Fewest Stops")
        if route.has_stairs:
            route.labels.append("Has Stairs")
        else:
            route.labels.append("No Stairs")
        if route.has_lift:
            route.labels.append("Uses Lifts")
        if route.has_escalator:
            route.labels.append("Uses Escalators")


def format_time(seconds: float) -> str:
    seconds = round(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    if secs == 0:
        return f"{minutes}m"
    return f"{minutes}m {secs}s"

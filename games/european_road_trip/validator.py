"""Judge a proposed route. The judge computes the cost; agents never declare it."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Optional


@dataclass
class RouteCheck:
    valid: bool
    km: Optional[int] = None
    reason: str = ""


def check_route(path, graph, start: str, required, max_length: int = 5000) -> RouteCheck:
    """Check one complete route: every road travelled must be listed in `path`."""
    if not isinstance(path, list) or not path:
        return RouteCheck(False, reason="route must be a non-empty list of city ids")
    if len(path) > max_length:
        return RouteCheck(False, reason=f"route longer than {max_length} cities")
    if not all(isinstance(city, str) for city in path):
        return RouteCheck(False, reason="every city id must be a string")
    unknown = next((city for city in path if city not in graph.cities), None)
    if unknown is not None:
        return RouteCheck(False, reason=f"unknown city: {unknown}")
    if path[0] != start:
        return RouteCheck(False, reason=f"route must start in {start}")
    if path[-1] != start:
        return RouteCheck(False, reason=f"route must end in {start}")
    middle = path[1:-1]
    if start in middle:
        return RouteCheck(False, reason=f"route may pass through {start} only at the start and the end")
    repeated = next((city for city, times in Counter(middle).items() if times > 1), None)
    if repeated is not None:
        return RouteCheck(False, reason=f"route passes through {repeated} more than once")
    missing = sorted(set(required) - set(path))
    if missing:
        return RouteCheck(False, reason="missing required cities: " + ", ".join(missing))
    total = 0
    for origin, destination in zip(path, path[1:]):
        road = graph.km(origin, destination)
        if road is None:
            return RouteCheck(False, reason=f"no road from {origin} to {destination}")
        total += road
    return RouteCheck(True, km=total)

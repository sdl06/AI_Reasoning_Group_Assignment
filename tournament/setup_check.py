"""Confirm the environment before a match, so problems appear before the clock runs."""
from __future__ import annotations

import platform
import sys
from importlib import metadata

EXPECTED = {"chess": "1.11.2", "catanatron": "3.2.1"}


def verify_environment() -> bool:
    """Prints what was checked. Returns True when everything is ready."""
    from games.european_road_trip.engine import RoadGraph

    healthy = True
    print(f"Python {platform.python_version()} on {platform.system()}")
    if sys.version_info < (3, 10):
        print("  PROBLEM: Python 3.10 or newer is required")
        healthy = False
    for package, expected in EXPECTED.items():
        try:
            found = metadata.version(package)
        except metadata.PackageNotFoundError:
            print(f"  PROBLEM: {package} is not installed")
            healthy = False
            continue
        same = found == expected
        print(f"  {package} {found}" + ("" if same else f" (expected {expected}, so rules or replays may differ)"))
        healthy = healthy and same
    graph = RoadGraph.load()
    issues = graph.problems()
    print(f"  Road map: {len(graph.cities)} cities, {len(graph.roads)} roads")
    for issue in issues:
        print(f"  PROBLEM: {issue}")
    healthy = healthy and not issues
    print("Ready." if healthy else "NOT ready: fix the problems above before playing.")
    return healthy

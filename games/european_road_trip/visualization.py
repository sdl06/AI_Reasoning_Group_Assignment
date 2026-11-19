"""Maps of the final routes: interactive when possible, self-contained always."""
from __future__ import annotations

import html
import math

from .engine import RoadGraph

COLORS = {"A": "#d1495b", "B": "#00798c"}


def route_svg(graph: RoadGraph, required, routes: dict, names: dict, width: int = 760) -> str:
    """A map drawn from coordinates alone. It needs no internet connection."""
    lats = [c["lat"] for c in graph.cities.values()]
    lons = [c["lon"] for c in graph.cities.values()]
    scale_x = math.cos(math.radians(sum(lats) / len(lats)))
    margin = 18
    right_margin = 70  # room for the names of the easternmost cities
    span_x = (max(lons) - min(lons)) * scale_x
    span_y = max(lats) - min(lats)
    factor = (width - margin - right_margin) / span_x
    height = int(span_y * factor + 2 * margin + 28)

    def xy(city):
        c = graph.cities[city]
        return (margin + (c["lon"] - min(lons)) * scale_x * factor, margin + (max(lats) - c["lat"]) * factor)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background:#f7f7f2;font-family:sans-serif">']
    for road in graph.roads:
        (x1, y1), (x2, y2) = xy(road["from"]), xy(road["to"])
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#d8d8d0" stroke-width="1"/>')
    for side, offset in (("A", -1.5), ("B", 1.5)):
        path = routes.get(side, {}).get("path")
        if not path:
            continue
        points = " ".join(f"{xy(city)[0] + offset:.1f},{xy(city)[1] + offset:.1f}" for city in path)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{COLORS[side]}" stroke-width="2.2" stroke-opacity="0.85"/>')
    required = set(required)
    for city in graph.cities:
        x, y = xy(city)
        radius = 4 if city in required else 1.8
        fill = "#222" if city in required else "#999"
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill}"><title>{html.escape(graph.cities[city]["name"])}</title></circle>')
        if city in required:
            parts.append(f'<text x="{x + 5:.1f}" y="{y - 4:.1f}" font-size="10" fill="#222">{html.escape(graph.cities[city]["name"])}</text>')
    y_text = height - 10
    x_text = margin
    for side in ("A", "B"):
        km = routes.get(side, {}).get("km")
        label = f"{names[side]}: {km:,} km" if km is not None else f"{names[side]}: no valid route"
        parts.append(f'<rect x="{x_text}" y="{y_text - 9}" width="14" height="4" fill="{COLORS[side]}"/>')
        parts.append(f'<text x="{x_text + 19}" y="{y_text}" font-size="12" fill="#222">{html.escape(label)}</text>')
        x_text += 300
    parts.append("</svg>")
    return "".join(parts)


def route_folium(graph: RoadGraph, required, routes: dict, names: dict):
    """Interactive map, or None if folium is not installed."""
    try:
        import folium
    except ImportError:
        return None
    # No background tiles: public tile servers refuse requests from notebooks (403 in Colab),
    # and a key would have to ship to students. Everything drawn here comes from our own map.
    world = folium.Map(tiles=None, zoom_snap=0.25)
    world.get_root().header.add_child(folium.Element("<style>.leaflet-container{background:#f7f7f2 !important}</style>"))
    all_roads = [[[graph.cities[r["from"]]["lat"], graph.cities[r["from"]]["lon"]], [graph.cities[r["to"]]["lat"], graph.cities[r["to"]]["lon"]]] for r in graph.roads]
    folium.PolyLine(all_roads, color="#c8c8c0", weight=1).add_to(world)
    required = set(required)
    shown = set(required)
    for side in ("A", "B"):
        route = routes.get(side, {})
        path = route.get("path")
        text = f"{names[side]}: {route['km']:,} km" if path else f"{names[side]}: no valid route"
        swatch = f'<span style="color:{COLORS[side]}">&#9644;</span>'
        layer = folium.FeatureGroup(name=f"{swatch} {html.escape(text)}").add_to(world)
        if path:
            points = [[graph.cities[c]["lat"], graph.cities[c]["lon"]] for c in path]
            folium.PolyLine(points, color=COLORS[side], weight=3, opacity=0.8, tooltip=html.escape(text)).add_to(layer)
            shown.update(path)
    for city in required:
        c = graph.cities[city]
        name = html.escape(c["name"])
        folium.CircleMarker([c["lat"], c["lon"]], radius=4, color="#222", fill=True, tooltip=name).add_to(world)
        label = f'<div style="font:600 11px sans-serif;color:#222;text-shadow:0 0 3px #fff,0 0 3px #fff">{name}</div>'
        folium.Marker([c["lat"], c["lon"]], icon=folium.features.DivIcon(icon_size=(120, 14), icon_anchor=(-7, 16), html=label)).add_to(world)
    folium.LayerControl(collapsed=False).add_to(world)
    lats, lons = [graph.cities[c]["lat"] for c in shown], [graph.cities[c]["lon"] for c in shown]
    world.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(32, 32))
    return world


def show(result: dict, names: dict) -> None:
    from IPython.display import HTML, display

    graph = RoadGraph.load()
    details = result["details"]
    required, routes = details["instance"]["required"], details["routes"]
    world = route_folium(graph, required, routes, names)
    drawing = route_svg(graph, required, routes, names)
    if world is None:
        display(HTML(drawing))
        return
    display(world)
    display(HTML(f"<details><summary>Map that works without internet</summary>{drawing}</details>"))

"""A plain schematic of the final board, with each player's points and cards."""
from __future__ import annotations

import html
import math

RESOURCE_COLORS = {"WOOD": "#4f772d", "BRICK": "#bc6c25", "SHEEP": "#a7c957", "WHEAT": "#e9c46a", "ORE": "#8d99ae", None: "#e6dcc3"}
PLAYER_COLORS = {"A": "#d1495b", "B": "#00798c"}
NODE_OFFSETS = {
    "NORTH": (0, -1),
    "NORTHEAST": (math.sqrt(3) / 2, -0.5),
    "SOUTHEAST": (math.sqrt(3) / 2, 0.5),
    "SOUTH": (0, 1),
    "SOUTHWEST": (-math.sqrt(3) / 2, 0.5),
    "NORTHWEST": (-math.sqrt(3) / 2, -0.5),
}
HEX_ORDER = ("NORTH", "NORTHEAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "NORTHWEST")


def board_svg(snapshot: dict, names: dict, size: float = 44) -> str:
    """Pointy-top hexes placed from Catanatron's cube coordinates."""

    def center(tile):
        x, y, z = tile
        return size * math.sqrt(3) / 2 * (x - y), size * 1.5 * z

    node_xy = {}
    for tile in snapshot["tiles"]:
        cx, cy = center(tile["tile"])
        for ref, node in tile["nodes"].items():
            dx, dy = NODE_OFFSETS[ref]
            node_xy[int(node)] = (cx + dx * size, cy + dy * size)
    xs = [x for x, _ in node_xy.values()]
    ys = [y for _, y in node_xy.values()]
    pad = 20
    left, top = min(xs) - pad, min(ys) - pad
    width, height = max(xs) - left + pad, max(ys) - top + pad

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="{left:.1f} {top:.1f} {width:.1f} {height:.1f}" style="font-family:sans-serif">']
    for tile in snapshot["tiles"]:
        cx, cy = center(tile["tile"])
        corners = " ".join(f"{cx + NODE_OFFSETS[r][0] * size:.1f},{cy + NODE_OFFSETS[r][1] * size:.1f}" for r in HEX_ORDER)
        parts.append(f'<polygon points="{corners}" fill="{RESOURCE_COLORS[tile["resource"]]}" stroke="#fff" stroke-width="2"/>')
        if tile["number"] is not None:
            fill = "#b00020" if tile["number"] in (6, 8) else "#222"
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="#fff"/>')
            parts.append(f'<text x="{cx:.1f}" y="{cy + 5:.1f}" font-size="14" text-anchor="middle" fill="{fill}">{tile["number"]}</text>')
        if tile["tile"] == snapshot["robber_tile"]:
            parts.append(f'<circle cx="{cx + 20:.1f}" cy="{cy - 18:.1f}" r="7" fill="#222"><title>Robber</title></circle>')
    for side in ("A", "B"):
        player = snapshot["players"][side]
        color = PLAYER_COLORS[side]
        for a, b in player["roads"]:
            if a in node_xy and b in node_xy:
                (x1, y1), (x2, y2) = node_xy[a], node_xy[b]
                parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="5"/>')
        for node in player["settlements"]:
            x, y = node_xy[node]
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        for node in player["cities"]:
            x, y = node_xy[node]
            parts.append(f'<rect x="{x - 9:.1f}" y="{y - 9:.1f}" width="18" height="18" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
    parts.append("</svg>")
    return "".join(parts)


def players_table(snapshot: dict, names: dict) -> str:
    rows = []
    for side in ("A", "B"):
        player = snapshot["players"][side]
        cards = ", ".join(f"{k.title()}: {v}" for k, v in player["resources"].items())
        dev = ", ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in player["development_cards"].items() if v) or "none"
        rows.append(
            f'<tr><td style="color:{PLAYER_COLORS[side]};font-weight:bold">{html.escape(names[side])}</td>'
            f"<td>{player['victory_points']}</td><td>{len(player['settlements'])}</td><td>{len(player['cities'])}</td>"
            f"<td>{len(player['roads'])}</td><td>{html.escape(cards)}</td><td>{html.escape(dev)}</td></tr>"
        )
    return ("<table cellpadding='6'><tr><th>Team</th><th>VP</th><th>Settlements</th><th>Cities</th><th>Roads</th>"
            "<th>Resources</th><th>Development cards</th></tr>" + "".join(rows) + "</table>")


def legend() -> str:
    items = "".join(
        f'<span style="display:inline-block;width:12px;height:12px;background:{color};margin:0 4px 0 12px"></span>{(resource or "desert").lower()}'
        for resource, color in RESOURCE_COLORS.items()
    )
    return f"<p>Circle: settlement. Square: city. Line: road. Black dot: robber.<br>{items}</p>"


def show(result: dict, names: dict) -> None:
    from IPython.display import HTML, display

    snapshot = result["details"].get("snapshot")
    if snapshot:
        display(HTML(f"<p>Final board after {snapshot['rounds']} rounds.</p>" + legend()))
        display(HTML(board_svg(snapshot, names)))
        display(HTML(players_table(snapshot, names)))

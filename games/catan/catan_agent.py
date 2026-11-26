"""Catan Tournament 1v1 agent. Team: AI_Reasoning_Group

Playbook: docs/students/CATAN_PLAYBOOK.md
Full rules: games/catan/README.md
Samples: docs/students/sample_observations/catan_*.json
Training: docs/students/TRAINING.md

You may not import catanatron.players. Values learned offline must live in this file.
"""
import random
from collections import Counter

# Learned Q-table is filled in Step 5 (offline training). Key: "features|ACTION_TYPE".
Q = {}

PIPS = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
RESOURCES = ("WOOD", "BRICK", "SHEEP", "WHEAT", "ORE")
BUILD_COSTS = {
    "BUILD_ROAD": {"WOOD": 1, "BRICK": 1},
    "BUILD_SETTLEMENT": {"WOOD": 1, "BRICK": 1, "SHEEP": 1, "WHEAT": 1},
    "BUILD_CITY": {"WHEAT": 2, "ORE": 3},
    "BUY_DEVELOPMENT_CARD": {"SHEEP": 1, "WHEAT": 1, "ORE": 1},
}

# Prefer VP and productive builds; trades only when they unlock something.
PRIORITY = [
    "BUILD_CITY",
    "BUILD_SETTLEMENT",
    "PLAY_KNIGHT_CARD",
    "PLAY_YEAR_OF_PLENTY",
    "PLAY_MONOPOLY",
    "PLAY_ROAD_BUILDING",
    "BUY_DEVELOPMENT_CARD",
    "BUILD_ROAD",
    "MARITIME_TRADE",
    "ROLL",
    "MOVE_ROBBER",
    "END_TURN",
]


def act(observation):
    """Called at each decision. Return {"action": <legal id>}."""
    return {"action": heuristic_policy(observation)}


# ---------------------------------------------------------------------------------
# Board / resource helpers
# ---------------------------------------------------------------------------------


def _vp_bucket(vp):
    if vp <= 2:
        return 0
    if vp <= 4:
        return 1
    if vp <= 6:
        return 2
    return 3


def _hand_bucket(n):
    if n <= 3:
        return 0
    if n <= 7:
        return 1
    return 2


def _resource_shape(resources):
    road = resources.get("WOOD", 0) + resources.get("BRICK", 0)
    city = resources.get("WHEAT", 0) + resources.get("ORE", 0)
    if road >= city + 2:
        return "road"
    if city >= road + 2:
        return "city"
    return "mixed"


def _action_types(observation):
    return {a["type"] for a in observation["actions"]}


def _action_by_id(observation, action_id):
    for action in observation["actions"]:
        if action["id"] == action_id:
            return action
    return None


def _q_key(features, action_type):
    return f"{features}|{action_type}"


def _tile_key(tile):
    return tuple(tile) if isinstance(tile, (list, tuple)) else tile


def _node_info(board):
    """Per-node pip total, resource set, and whether a port touches the node."""
    production = {}
    resources = {}
    for tile in board["tiles"]:
        pips = PIPS.get(tile.get("number"), 0)
        res = tile.get("resource")
        for node in tile["nodes"]:
            production[node] = production.get(node, 0) + pips
            resources.setdefault(node, set())
            if res:
                resources[node].add(res)
    ports = {}
    for port in board.get("ports", []):
        for node in port["nodes"]:
            ports[node] = port.get("resource")  # None => 3:1
    return production, resources, ports


def _node_score(node, production, resources, ports, prefer_missing=None):
    score = float(production.get(node, 0))
    kinds = resources.get(node, set())
    score += 1.5 * len(kinds)
    if node in ports:
        score += 2.0 if ports[node] is None else 1.5
    if prefer_missing:
        score += 2.0 * len(kinds & prefer_missing)
    # Mild preference for balanced numbers already in production via pips.
    return score


def _owned_resources(me):
    have = set()
    production, resources, _ = None, None, None
    # Settlements/cities imply resources from adjacent tiles — caller passes board.
    return have


def _my_resource_kinds(observation):
    """Resources my settlements/cities currently touch."""
    production, resources, _ports = _node_info(observation["board"])
    me = observation["me"]
    kinds = set()
    for node in me.get("settlements", []) + me.get("cities", []):
        kinds |= resources.get(node, set())
    return kinds


def _edge_key(edge):
    return tuple(sorted(edge))


def _road_toward_score(edge, production, resources, ports, my_nodes, occupied):
    """Prefer roads that reach a high-value empty node we do not already own."""
    a, b = edge
    score = 0.0
    for node in (a, b):
        if node in my_nodes or node in occupied:
            continue
        score = max(score, _node_score(node, production, resources, ports))
    # Slight bonus for extending from our network
    if a in my_nodes or b in my_nodes:
        score += 0.5
    return score


def _occupied_nodes(observation):
    occupied = set()
    for side in ("me", "opponent"):
        player = observation[side]
        occupied.update(player.get("settlements", []))
        occupied.update(player.get("cities", []))
    return occupied


def _my_nodes(observation):
    me = observation["me"]
    return set(me.get("settlements", [])) | set(me.get("cities", []))


def _tile_pips(board):
    out = {}
    for tile in board["tiles"]:
        out[_tile_key(tile["tile"])] = PIPS.get(tile.get("number"), 0)
    return out


def _opponent_nodes_on_tile(board, tile_coord, opponent):
    nodes = set()
    key = _tile_key(tile_coord)
    for tile in board["tiles"]:
        if _tile_key(tile["tile"]) == key:
            nodes = set(tile["nodes"])
            break
    opp = set(opponent.get("settlements", [])) | set(opponent.get("cities", []))
    return nodes & opp


def _can_afford_after_trade(resources, trade):
    """Return new resource counts if we apply a maritime trade, else None."""
    have = Counter(resources)
    give, n, recv = trade["give"], trade["give_count"], trade["receive"]
    if have[give] < n:
        return None
    have[give] -= n
    have[recv] += 1
    return have


def _unlocks_build(have, action_types):
    """Which valuable builds become affordable with this hand."""
    unlocked = []
    for kind, cost in BUILD_COSTS.items():
        if kind not in action_types and kind.startswith("BUILD"):
            # action may not be listed until resources match; check affordability
            pass
        if all(have.get(r, 0) >= c for r, c in cost.items()):
            unlocked.append(kind)
    return unlocked


def _affordable_builds(resources):
    have = resources if isinstance(resources, Counter) else Counter(resources)
    return [
        kind
        for kind, cost in BUILD_COSTS.items()
        if all(have.get(r, 0) >= c for r, c in cost.items())
    ]


def _missing_for(cost, resources):
    have = resources if isinstance(resources, dict) else dict(resources)
    return {r: c - have.get(r, 0) for r, c in cost.items() if have.get(r, 0) < c}


# ---------------------------------------------------------------------------------
# Required algorithms
# ---------------------------------------------------------------------------------


def state_features(observation):
    """Coarse, deterministic abstraction for tabular Q-learning."""
    me = observation["me"]
    opp = observation["opponent"]
    types = _action_types(observation)
    resources = me.get("resources") or {}
    return [
        observation.get("phase", "?"),
        _vp_bucket(me.get("victory_points", me.get("visible_victory_points", 0))),
        _vp_bucket(opp.get("visible_victory_points", 0)),
        int("BUILD_CITY" in types),
        int("BUILD_SETTLEMENT" in types),
        int("BUILD_ROAD" in types),
        int("BUY_DEVELOPMENT_CARD" in types),
        _resource_shape(resources),
        _hand_bucket(me.get("resource_cards", sum(resources.values()) if resources else 0)),
    ]


def action_value(observation, action_id):
    """Q-table lookup by state features + action type; missing keys are 0.0."""
    action = _action_by_id(observation, action_id)
    if action is None:
        return 0.0
    key = _q_key(state_features(observation), action["type"])
    return float(Q.get(key, 0.0))


def q_update(q, reward, best_next_q, alpha, gamma):
    """One Q-learning update. Returns the new value for Q(s, a)."""
    return q + alpha * (reward + gamma * best_next_q - q)


def heuristic_policy(observation):
    """Strong baseline: scored placement, robber, builds, unlock-only trades."""
    actions = observation["actions"]
    if not actions:
        raise ValueError("no legal actions")

    phase = observation.get("phase")
    production, resources, ports = _node_info(observation["board"])

    if phase == "initial_placement":
        return _pick_initial(observation, actions, production, resources, ports)

    if phase == "move_robber":
        return _pick_robber(observation, actions)

    if phase == "free_roads":
        return _pick_road(observation, actions, production, resources, ports)

    # play_turn (and any other)
    return _pick_play_turn(observation, actions, production, resources, ports)


# ---------------------------------------------------------------------------------
# Heuristic decisions
# ---------------------------------------------------------------------------------


def _pick_initial(observation, actions, production, resources, ports):
    if actions[0]["type"] == "BUILD_SETTLEMENT":
        have = _my_resource_kinds(observation)
        prefer = set(RESOURCES) - have
        return max(
            actions,
            key=lambda a: _node_score(a["node"], production, resources, ports, prefer),
        )["id"]
    # Road after settlement: point toward best empty neighbour
    occupied = _occupied_nodes(observation)
    my_nodes = _my_nodes(observation)
    return max(
        actions,
        key=lambda a: _road_toward_score(
            a["edge"], production, resources, ports, my_nodes, occupied
        ),
    )["id"]


def _pick_robber(observation, actions):
    tile_pips = _tile_pips(observation["board"])
    opp = observation["opponent"]

    def score(a):
        s = 0.0
        if a.get("steal_from") == "opponent":
            s += 20.0
        s += tile_pips.get(_tile_key(a["tile"]), 0)
        # Prefer tiles where opponent actually sits
        if _opponent_nodes_on_tile(observation["board"], a["tile"], opp):
            s += 5.0
        # Avoid our own high production if we can (steal_from null and we touch it)
        return s

    return max(actions, key=score)["id"]


def _pick_road(observation, actions, production, resources, ports):
    occupied = _occupied_nodes(observation)
    my_nodes = _my_nodes(observation)
    return max(
        actions,
        key=lambda a: _road_toward_score(
            a["edge"], production, resources, ports, my_nodes, occupied
        ),
    )["id"]


def _pick_settlement(actions, production, resources, ports, prefer_missing):
    return max(
        actions,
        key=lambda a: _node_score(a["node"], production, resources, ports, prefer_missing),
    )["id"]


def _pick_city(actions, production, resources, ports):
    # Cities upgrade settlements; prefer highest production settlement node
    return max(
        actions,
        key=lambda a: _node_score(a["node"], production, resources, ports),
    )["id"]


def _trade_unlocks_something(observation, trade):
    """True if this maritime trade newly enables a build or buy_dev this turn."""
    me_res = observation["me"].get("resources") or {}
    before = set(_affordable_builds(me_res))
    after_hand = _can_afford_after_trade(me_res, trade)
    if after_hand is None:
        return False
    after = set(_affordable_builds(after_hand))
    valuable = {"BUILD_CITY", "BUILD_SETTLEMENT", "BUY_DEVELOPMENT_CARD", "BUILD_ROAD"}
    return bool((after - before) & valuable)


def _pick_trade(observation, actions):
    useful = [a for a in actions if _trade_unlocks_something(observation, a)]
    if not useful:
        return None
    # Prefer trades that unlock city, then settlement, then road/dev
    rank = {
        "BUILD_CITY": 4,
        "BUILD_SETTLEMENT": 3,
        "BUY_DEVELOPMENT_CARD": 2,
        "BUILD_ROAD": 1,
    }

    def score(a):
        me_res = observation["me"].get("resources") or {}
        before = set(_affordable_builds(me_res))
        after = set(_affordable_builds(_can_afford_after_trade(me_res, a)))
        gained = after - before
        return max((rank.get(g, 0) for g in gained), default=0)

    return max(useful, key=score)["id"]


def _pick_dev_play(observation, actions, kind):
    if kind == "PLAY_MONOPOLY":
        # Target a resource we likely need for the next build
        me_res = observation["me"].get("resources") or {}
        missing = _missing_for(BUILD_COSTS["BUILD_CITY"], me_res)
        if not missing:
            missing = _missing_for(BUILD_COSTS["BUILD_SETTLEMENT"], me_res)
        if missing:
            target = max(missing, key=missing.get)
            for a in actions:
                if a.get("resource") == target:
                    return a["id"]
        return actions[0]["id"]

    if kind == "PLAY_YEAR_OF_PLENTY":
        me_res = observation["me"].get("resources") or {}
        # Prefer the listed option whose resources most help city then settlement
        def yop_score(a):
            gained = Counter(a.get("resources") or [])
            trial = Counter(me_res) + gained
            score = 0
            if "BUILD_CITY" in _affordable_builds(trial):
                score += 10
            if "BUILD_SETTLEMENT" in _affordable_builds(trial):
                score += 6
            if "BUY_DEVELOPMENT_CARD" in _affordable_builds(trial):
                score += 3
            return score

        return max(actions, key=yop_score)["id"]

    return actions[0]["id"]


def _pick_play_turn(observation, actions, production, resources, ports):
    types = _action_types(observation)
    prefer = set(RESOURCES) - _my_resource_kinds(observation)
    me = observation["me"]
    vp = me.get("victory_points", 0)
    vps_to_win = observation.get("vps_to_win", 7)

    # Endgame: if a build wins or reaches 6+, prioritise VP actions hard
    urgent_city = vp >= vps_to_win - 2
    urgent_settle = vp >= vps_to_win - 1

    for kind in PRIORITY:
        options = [a for a in actions if a["type"] == kind]
        if not options:
            continue

        if kind == "BUILD_CITY":
            return _pick_city(options, production, resources, ports)

        if kind == "BUILD_SETTLEMENT":
            return _pick_settlement(options, production, resources, ports, prefer)

        if kind == "BUILD_ROAD":
            # Skip random roads if we are one VP from a settlement we cannot yet place
            # and a trade might be better — but if road is offered, take best direction.
            return _pick_road(observation, options, production, resources, ports)

        if kind == "MARITIME_TRADE":
            trade_id = _pick_trade(observation, options)
            if trade_id is not None:
                return trade_id
            continue  # do not trade for no reason

        if kind == "BUY_DEVELOPMENT_CARD":
            # Prefer city/settlement path when ore-poor late; still buy if offered
            if urgent_settle and "BUILD_SETTLEMENT" not in types and "BUILD_CITY" not in types:
                return options[0]["id"]
            if urgent_city and "BUILD_CITY" in types:
                continue
            return options[0]["id"]

        if kind in ("PLAY_KNIGHT_CARD", "PLAY_ROAD_BUILDING"):
            return options[0]["id"]

        if kind in ("PLAY_YEAR_OF_PLENTY", "PLAY_MONOPOLY"):
            return _pick_dev_play(observation, options, kind)

        if kind in ("ROLL", "END_TURN", "MOVE_ROBBER"):
            return options[0]["id"]

    return actions[0]["id"]

"""Catan Tournament 1v1 on Catanatron: legal actions, hidden information, adjudication.

Catanatron owns the rules. This module decides what each agent may see, turns
actions into plain JSON, and ends the game when a limit is reached. Note that
Catanatron's random numbers come from Python's global `random`, seeded by Game().
"""
from __future__ import annotations

import time

from catanatron import Color, Game
from catanatron.models.enums import ActionType, RESOURCES
from catanatron.models.map import LandTile, Port
from catanatron.models.player import SimplePlayer
from catanatron.state_functions import (
    get_actual_victory_points,
    get_largest_army,
    get_longest_road_color,
    get_longest_road_length,
    get_played_dev_cards,
    get_visible_victory_points,
    player_key,
    player_num_dev_cards,
    player_num_resource_cards,
)

from tournament.agents import AgentFailure
from tournament.scoring import SIDES, GameResult, incident, other, start_players
from tournament.timing import ChallengeTimeUp, TurnClocks

from .validator import parse_action

COLOR_OF = {"A": Color.RED, "B": Color.BLUE}
SIDE_OF = {color: side for side, color in COLOR_OF.items()}
DEV_CARDS = ("KNIGHT", "YEAR_OF_PLENTY", "MONOPOLY", "ROAD_BUILDING", "VICTORY_POINT")
BUILDING_COSTS = {
    "ROAD": {"WOOD": 1, "BRICK": 1},
    "SETTLEMENT": {"WOOD": 1, "BRICK": 1, "SHEEP": 1, "WHEAT": 1},
    "CITY": {"WHEAT": 2, "ORE": 3},
    "DEVELOPMENT_CARD": {"SHEEP": 1, "WHEAT": 1, "ORE": 1},
}


def new_game(seed: int, vps_to_win: int = 7) -> Game:
    return Game([SimplePlayer(COLOR_OF["A"]), SimplePlayer(COLOR_OF["B"])], seed=seed, vps_to_win=vps_to_win)


def _relation(color, viewer_color) -> str:
    return "me" if color == viewer_color else "opponent"


def action_to_json(action, viewer_color) -> dict:
    """The agent-facing description of a legal action. No hidden data can appear here."""
    kind = action.action_type
    data = {"type": kind.value}
    value = action.value
    if kind in (ActionType.BUILD_SETTLEMENT, ActionType.BUILD_CITY):
        data["node"] = value
    elif kind == ActionType.BUILD_ROAD:
        data["edge"] = sorted(value)
    elif kind == ActionType.MOVE_ROBBER:
        data["tile"] = list(value[0])
        data["steal_from"] = _relation(value[1], viewer_color) if value[1] is not None else None
    elif kind == ActionType.PLAY_YEAR_OF_PLENTY:
        data["resources"] = list(value)
    elif kind == ActionType.PLAY_MONOPOLY:
        data["resource"] = value
    elif kind == ActionType.MARITIME_TRADE:
        given = [card for card in value[:-1] if card is not None]
        data.update(give=given[0], give_count=len(given), receive=value[-1])
    return data


def _sort_key(action) -> str:
    # Catanatron builds some action lists from sets, whose order changes between runs.
    return f"{action.action_type.value}|{sorted(action.value) if action.action_type == ActionType.BUILD_ROAD else action.value!r}"


def legal_actions(game: Game) -> list:
    return sorted(game.state.playable_actions, key=_sort_key)


def public_log_entry(logged, viewer_color) -> dict:
    """What a viewer legitimately knows about one finished action."""
    kind = logged.action_type
    entry = {"player": _relation(logged.color, viewer_color), "type": kind.value}
    value = logged.value
    if kind == ActionType.ROLL:
        entry["dice"] = list(value)
    elif kind in (ActionType.BUILD_SETTLEMENT, ActionType.BUILD_CITY):
        entry["node"] = value
    elif kind == ActionType.BUILD_ROAD:
        entry["edge"] = sorted(value)
    elif kind == ActionType.MOVE_ROBBER:
        entry["tile"] = list(value[0])
        entry["stole_from"] = _relation(value[1], viewer_color) if value[1] is not None else None
        if value[1] is not None and viewer_color in (logged.color, value[1]):
            entry["stolen_resource"] = value[2]  # only thief and victim know the card
    elif kind == ActionType.BUY_DEVELOPMENT_CARD and logged.color == viewer_color:
        entry["card"] = value  # only the buyer knows the card
    elif kind == ActionType.DISCARD:
        entry["count"] = len(value)
        if logged.color == viewer_color:
            entry["cards"] = list(value)
    elif kind == ActionType.PLAY_YEAR_OF_PLENTY:
        entry["resources"] = list(value)
    elif kind == ActionType.PLAY_MONOPOLY:
        entry["resource"] = value
    elif kind == ActionType.MARITIME_TRADE:
        given = [card for card in value[:-1] if card is not None]
        entry.update(give=given[0], give_count=len(given), receive=value[-1])
    return entry


def _public_log(game: Game, color) -> list:
    """Each player's view of the log, extended only with the actions it has not seen yet."""
    logs = game.__dict__.setdefault("_public_logs", {})
    entries = logs.setdefault(color, [])
    for logged in game.state.actions[len(entries):]:
        entries.append(public_log_entry(logged, color))
    return list(entries)


def board_description(game: Game) -> dict:
    """The board layout. It never changes during a game, so it is built only once."""
    cached = getattr(game, "_board_description", None)
    if cached is None:
        cached = game._board_description = _describe_board(game)
    return cached


def _describe_board(game: Game) -> dict:
    catan_map = game.state.board.map
    tiles, ports = [], []
    for coordinate, tile in catan_map.tiles.items():
        if isinstance(tile, LandTile):
            tiles.append({
                "tile": list(coordinate),
                "resource": tile.resource,
                "number": tile.number,
                "nodes": sorted(tile.nodes.values()),
                "edges": sorted(sorted(edge) for edge in tile.edges.values()),
            })
        elif isinstance(tile, Port):
            ports.append({"resource": tile.resource, "nodes": sorted(catan_map.port_nodes[tile.resource] & set(tile.nodes.values()))})
    return {"tiles": sorted(tiles, key=lambda t: t["tile"]), "ports": sorted(ports, key=lambda p: (p["resource"] or "", p["nodes"]))}


def _buildings(game: Game, color, kind: str) -> list:
    return sorted(game.state.buildings_by_color[color].get(kind, []))


def _roads(game: Game, color) -> list:
    return sorted({tuple(sorted(edge)) for edge, owner in game.state.board.roads.items() if owner == color})


def player_public_info(game: Game, color) -> dict:
    """Facts about a player that everyone at the table can see."""
    state = game.state
    return {
        "visible_victory_points": get_visible_victory_points(state, color),
        "settlements": _buildings(game, color, "SETTLEMENT"),
        "cities": _buildings(game, color, "CITY"),
        "roads": [list(edge) for edge in _roads(game, color)],
        "resource_cards": player_num_resource_cards(state, color),
        "development_cards": player_num_dev_cards(state, color),
        "played_development_cards": {card: get_played_dev_cards(state, color, card) for card in DEV_CARDS},
        "longest_road_length": get_longest_road_length(state, color),
        "has_longest_road": get_longest_road_color(state) == color,
        "has_largest_army": get_largest_army(state)[0] == color,
    }


def _phase(state) -> str:
    if state.is_initial_build_phase:
        return "initial_placement"
    if state.current_prompt.value == "MOVE_ROBBER":
        return "move_robber"
    if state.current_prompt.value == "DISCARD":
        return "discard"
    if state.is_road_building:
        return "free_roads"
    return "play_turn"


def observation_for(game: Game, side: str, actions: list, clocks=None, config: dict = None) -> dict:
    """Everything the agent on `side` may know. Never the rival's hand or cards."""
    state = game.state
    color = COLOR_OF[side]
    key = player_key(state, color)
    config = config or {}
    my_info = player_public_info(game, color)
    my_info.update(
        victory_points=get_actual_victory_points(state, color),
        resources={resource: state.player_state[f"{key}_{resource}_IN_HAND"] for resource in RESOURCES},
        development_cards_in_hand={card: state.player_state[f"{key}_{card}_IN_HAND"] for card in DEV_CARDS},
    )
    return {
        "game": "catan",
        "phase": _phase(state),
        "round": state.num_turns // 2,
        "vps_to_win": game.vps_to_win,
        "max_rounds": config.get("max_rounds"),
        "actions": [{"id": index, **action_to_json(action, color)} for index, action in enumerate(actions)],
        "me": my_info,
        "opponent": player_public_info(game, COLOR_OF[other(side)]),
        "board": board_description(game),
        "robber_tile": list(state.board.robber_coordinate),
        "development_cards_left": len(state.development_listdeck),
        "building_costs": BUILDING_COSTS,
        "log": _public_log(game, color),
        "time_remaining_s": round(clocks.remaining[side], 3) if clocks else None,
    }


def victory_points(game: Game) -> dict:
    return {side: get_actual_victory_points(game.state, COLOR_OF[side]) for side in SIDES}


def adjudicate(game: Game):
    """Limit reached with no winner: the published criteria decide, or it is a draw."""
    state = game.state

    def facts(side):
        color = COLOR_OF[side]
        return (
            ("more_victory_points", get_actual_victory_points(state, color)),
            ("more_cities", len(_buildings(game, color, "CITY"))),
            ("more_settlements", len(_buildings(game, color, "SETTLEMENT"))),
            ("more_resources", player_num_resource_cards(state, color)),
        )

    for (name, a), (_, b) in zip(facts("A"), facts("B")):
        if a != b:
            return ("A" if a > b else "B"), name
    return None, "adjudicated_draw"


def snapshot(game: Game) -> dict:
    """What the visualization needs at the end of the game."""
    state = game.state
    catan_map = state.board.map
    tiles = []
    for coordinate, tile in catan_map.land_tiles.items():
        tiles.append({"tile": list(coordinate), "resource": tile.resource, "number": tile.number,
                      "nodes": {ref.value: node for ref, node in tile.nodes.items()}})
    players = {}
    for side in SIDES:
        color = COLOR_OF[side]
        key = player_key(state, color)
        players[side] = {
            "victory_points": get_actual_victory_points(state, color),
            "settlements": _buildings(game, color, "SETTLEMENT"),
            "cities": _buildings(game, color, "CITY"),
            "roads": [list(edge) for edge in _roads(game, color)],
            "resources": {resource: state.player_state[f"{key}_{resource}_IN_HAND"] for resource in RESOURCES},
            "development_cards": {card: state.player_state[f"{key}_{card}_IN_HAND"] for card in DEV_CARDS},
        }
    return {"tiles": tiles, "robber_tile": list(state.board.robber_coordinate), "players": players, "rounds": state.num_turns // 2}


def _rival_also_fails(game: Game, failed_side: str, clocks, config: dict):
    """Play random-free forced moves on a copy until the rival must decide, then ask it once."""
    probe = game.copy()
    rival = other(failed_side)
    for _ in range(200):
        actions = legal_actions(probe)
        if not actions or probe.winning_color() is not None:
            return None
        current = SIDE_OF[probe.state.current_color()]
        if current == rival and len(actions) > 1:
            try:
                response = clocks.ask(rival, observation_for(probe, rival, actions, clocks, config))
                parse_action(response, len(actions))
            except AgentFailure as failure:
                return incident(rival, failure)
            except ChallengeTimeUp:
                return None
            return None
        probe.execute(actions[0])
    return None


def play_game(players: dict, config: dict, seed: int, names: dict = None, live=None) -> GameResult:
    """players maps "A"/"B" to unstarted players."""
    began = time.monotonic()
    names = names or {"A": "A", "B": "B"}
    failed = start_players(players, "catan", seed, "0 VP")
    if failed is not None:
        failed.duration_s = round(time.monotonic() - began, 2)
        return failed

    game = new_game(seed, config["vps_to_win"])
    clocks = TurnClocks(players, config["clock_s"], config["challenge_limit_s"])
    incidents = []
    decisions = {"A": 0, "B": 0}
    winner, reason = None, None
    try:
        while reason is None:
            champion = game.winning_color()
            if champion is not None:
                winner, reason = SIDE_OF[champion], "reached_victory_points"
                break
            if game.state.num_turns // 2 >= config["max_rounds"] or sum(decisions.values()) >= config["max_decisions"]:
                winner, reason = adjudicate(game)
                break
            actions = legal_actions(game)
            if not actions:
                winner, reason = adjudicate(game)
                incidents.append({"side": None, "kind": "engine", "detail": "no legal actions available"})
                break
            if len(actions) == 1:
                game.execute(actions[0])  # nothing to decide, so no time is charged
                continue
            side = SIDE_OF[game.state.current_color()]
            try:
                response = clocks.ask(side, observation_for(game, side, actions, clocks, config))
                choice = parse_action(response, len(actions))
            except AgentFailure as failure:
                incidents.append(incident(side, failure))
                second = _rival_also_fails(game, side, clocks, config)
                if second is not None:
                    incidents.append(second)
                    reason = "both_agents_failed"
                else:
                    winner, reason = other(side), failure.kind
                break
            decisions[side] += 1
            game.execute(actions[choice])
            if live is not None:
                points = victory_points(game)
                live.update(
                    f"CATAN  round {game.state.num_turns // 2}/{config['max_rounds']}\n"
                    f"{names['A']}: {points['A']} VP  ({clocks.remaining['A']:.1f} s left)\n"
                    f"{names['B']}: {points['B']} VP  ({clocks.remaining['B']:.1f} s left)"
                )
    except ChallengeTimeUp:
        winner, reason = adjudicate(game)
    finally:
        for player in players.values():
            player.stop()

    points = victory_points(game)
    if live is not None:
        live.update(f"CATAN finished: {names['A']} {points['A']} VP | {names['B']} {points['B']} VP", force=True)
    return GameResult(
        game="catan",
        winner=winner,
        reason=reason,
        score={side: f"{points[side]} VP" for side in SIDES},
        incidents=incidents,
        seed=seed,
        duration_s=round(time.monotonic() - began, 2),
        details={"snapshot": snapshot(game), "decisions": decisions,
                 "clock_left_s": {side: round(clocks.remaining[side], 2) for side in SIDES}},
    )

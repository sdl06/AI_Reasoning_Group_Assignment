"""Rules and match loop for Battleship with moving ships."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from tournament.agents import AgentFailure
from tournament.scoring import SIDES, GameResult, derive_seed, incident, other, start_players
from tournament.timing import ChallengeTimeUp, TurnClocks

from .validator import DIRECTIONS, check_placement, check_turn, ship_cells

FLEET = [("carrier", 5), ("battleship", 4), ("cruiser", 3), ("submarine", 3), ("destroyer", 2)]
TOTAL_SEGMENTS = sum(length for _, length in FLEET)


def sonar_distribution(true_count: int, region_cells: int, correct: float = 0.8) -> dict:
    """P(reading | true count). Readings outside 0..region_cells are impossible, so renormalise."""
    error = (1 - correct) / 2
    raw = {true_count: correct, true_count - 1: error, true_count + 1: error}
    valid = {reading: p for reading, p in raw.items() if 0 <= reading <= region_cells}
    total = sum(valid.values())
    return {reading: p / total for reading, p in sorted(valid.items())}


def sonar_region(center: tuple, board_size: int) -> list:
    """The 3 x 3 square around center, clipped at the edges of the board."""
    row, col = center
    return [
        (r, c)
        for r in range(row - 1, row + 2)
        for c in range(col - 1, col + 2)
        if 0 <= r < board_size and 0 <= c < board_size
    ]


@dataclass
class Ship:
    id: str
    length: int
    row: int
    col: int
    orientation: str
    damaged: set = field(default_factory=set)  # indexes of damaged segments

    @property
    def cells(self) -> list:
        return ship_cells(self.row, self.col, self.orientation, self.length)

    @property
    def immobile(self) -> bool:
        return bool(self.damaged)

    @property
    def sunk(self) -> bool:
        return len(self.damaged) == self.length


class Board:
    """One player's fleet and everything that player has learned so far."""

    def __init__(self, board_size: int, sonar_uses: int):
        self.board_size = board_size
        self.ships = []
        self.sonar_left = sonar_uses
        self.shots = []
        self.sonar_log = []
        self.damage = []

    def place(self, placements: list) -> None:
        lengths = dict(FLEET)
        self.ships = [Ship(p["ship"], lengths[p["ship"]], p["row"], p["col"], p["orientation"]) for p in placements]

    def occupied(self, ignore: Ship = None) -> set:
        cells = set()
        for ship in self.ships:
            if ship is not ignore:
                cells.update(ship.cells)
        return cells

    def legal_moves(self) -> list:
        moves = []
        for ship in self.ships:
            if ship.immobile:
                continue
            blocked = self.occupied(ignore=ship)
            for direction, (dr, dc) in DIRECTIONS.items():
                cells = ship_cells(ship.row + dr, ship.col + dc, ship.orientation, ship.length)
                inside = all(0 <= r < self.board_size and 0 <= c < self.board_size for r, c in cells)
                if inside and not blocked.intersection(cells):
                    moves.append({"ship": ship.id, "direction": direction})
        return moves

    def apply_move(self, move: dict) -> None:
        ship = next(s for s in self.ships if s.id == move["ship"])
        dr, dc = DIRECTIONS[move["direction"]]
        ship.row += dr
        ship.col += dc

    def receive_shot(self, target: tuple, turn: int) -> dict:
        for ship in self.ships:
            if target in ship.cells:
                segment = ship.cells.index(target)
                if segment in ship.damaged:
                    return {"result": "MISS", "already_damaged": True}
                ship.damaged.add(segment)
                result = "SUNK" if ship.sunk else "HIT"
                self.damage.append({"turn": turn, "cell": list(target), "ship": ship.id, "sunk": ship.sunk})
                return {"result": result, "sunk_length": ship.length} if ship.sunk else {"result": result}
        return {"result": "MISS"}

    def segments_destroyed(self) -> int:
        return sum(len(ship.damaged) for ship in self.ships)

    def ships_sunk(self) -> int:
        return sum(ship.sunk for ship in self.ships)

    def count_segments(self, cells: list) -> int:
        occupied = self.occupied()
        return sum(cell in occupied for cell in cells)

    def grid(self) -> str:
        """Compact picture for the replay: '.' water, 'S' ship, 'X' damaged."""
        rows = [["."] * self.board_size for _ in range(self.board_size)]
        for ship in self.ships:
            for index, (r, c) in enumerate(ship.cells):
                rows[r][c] = "X" if index in ship.damaged else "S"
        return "".join("".join(row) for row in rows)


class BattleshipGame:
    """The whole game state. Agents only ever see what observe() gives them."""

    def __init__(self, seed: int, board_size: int = 10, sonar_uses: int = 2, sonar_correct: float = 0.8, max_rounds: int = 150):
        self.seed = seed
        self.board_size = board_size
        self.sonar_uses = sonar_uses
        self.sonar_correct = sonar_correct
        self.max_rounds = max_rounds
        self.boards = {side: Board(board_size, sonar_uses) for side in SIDES}
        self.turn = 0
        # One stream per player, so one team's sonar noise never depends on the other's choices.
        self._sonar_rng = {side: random.Random(derive_seed(seed, f"sonar-{side}")) for side in SIDES}
        self._placement_rng = {side: random.Random(derive_seed(seed, f"placement-{side}")) for side in SIDES}

    def random_placements(self, side: str) -> list:
        rng = self._placement_rng[side]
        placements, occupied = [], set()
        for ship, length in FLEET:
            while True:
                orientation = rng.choice("HV")
                row = rng.randrange(self.board_size - (length - 1 if orientation == "V" else 0))
                col = rng.randrange(self.board_size - (length - 1 if orientation == "H" else 0))
                cells = ship_cells(row, col, orientation, length)
                if not occupied.intersection(cells):
                    occupied.update(cells)
                    placements.append({"ship": ship, "row": row, "col": col, "orientation": orientation})
                    break
        return placements

    def place(self, side: str, response) -> None:
        placements = check_placement(response, FLEET, self.board_size)
        self.boards[side].place(placements if placements is not None else self.random_placements(side))

    def placement_observation(self, side: str, clocks=None) -> dict:
        return {
            "game": "battleship",
            "phase": "placement",
            "board_size": self.board_size,
            "fleet": [{"ship": ship, "length": length} for ship, length in FLEET],
            "time_remaining_s": round(clocks.remaining[side], 3) if clocks else None,
        }

    def observe(self, side: str, clocks=None) -> dict:
        mine, rival = self.boards[side], self.boards[other(side)]
        return {
            "game": "battleship",
            "phase": "turn",
            "turn": self.turn,
            "max_rounds": self.max_rounds,
            "board_size": self.board_size,
            "my_ships": [
                {
                    "ship": ship.id,
                    "length": ship.length,
                    "orientation": ship.orientation,
                    "cells": [list(cell) for cell in ship.cells],
                    "damaged_cells": [list(ship.cells[i]) for i in sorted(ship.damaged)],
                    "immobile": ship.immobile,
                    "sunk": ship.sunk,
                }
                for ship in mine.ships
            ],
            "legal_moves": mine.legal_moves(),
            "my_shots": mine.shots,
            "my_sonar": mine.sonar_log,
            "sonar_remaining": mine.sonar_left,
            "sonar_correct_probability": self.sonar_correct,
            "enemy_ships_sunk": sorted(s["sunk_length"] for s in mine.shots if s["result"] == "SUNK"),
            "enemy_segments_destroyed": rival.segments_destroyed(),
            "damage_received": mine.damage,
            "time_remaining_s": round(clocks.remaining[side], 3) if clocks else None,
        }

    def apply_turn(self, side: str, response) -> dict:
        """Validate and apply one action: move first, then shot or sonar."""
        mine, rival = self.boards[side], self.boards[other(side)]
        action = check_turn(response, self.board_size, mine.legal_moves(), mine.sonar_left)
        self.turn += 1
        if action["move"] is not None:
            mine.apply_move(action["move"])
        if "sonar" in action:
            cells = sonar_region(action["sonar"], self.board_size)
            true_count = rival.count_segments(cells)
            model = sonar_distribution(true_count, len(cells), self.sonar_correct)
            reading = self._sonar_rng[side].choices(list(model), weights=list(model.values()))[0]
            mine.sonar_left -= 1
            entry = {"turn": self.turn, "center": list(action["sonar"]), "reading": reading}
            mine.sonar_log.append(entry)
            return {"side": side, "move": action["move"], **entry, "true_count": true_count}
        outcome = rival.receive_shot(action["shot"], self.turn)
        entry = {"turn": self.turn, "target": list(action["shot"]), **outcome}
        mine.shots.append(entry)
        return {"side": side, "move": action["move"], **entry}

    def finished(self, side: str) -> bool:
        return self.boards[other(side)].segments_destroyed() == TOTAL_SEGMENTS

    def adjudicate(self):
        """Time or round limit reached: the published criteria decide, or it is a draw."""
        a, b = self.boards["A"], self.boards["B"]
        criteria = [
            ("more_segments_destroyed", b.segments_destroyed(), a.segments_destroyed()),
            ("more_ships_sunk", b.ships_sunk(), a.ships_sunk()),
            ("fewer_own_segments_destroyed", -a.segments_destroyed(), -b.segments_destroyed()),
        ]
        for name, score_a, score_b in criteria:
            if score_a != score_b:
                return ("A" if score_a > score_b else "B"), name
        return None, "adjudicated_draw"

    def score(self) -> dict:
        return {
            side: f"{self.boards[other(side)].segments_destroyed()} hits, {self.boards[other(side)].ships_sunk()} sunk"
            for side in SIDES
        }


def _ask_placement(game, clocks, side):
    response = clocks.ask(side, game.placement_observation(side, clocks))
    game.place(side, response)


def play_game(players: dict, config: dict, seed: int, names: dict = None, live=None) -> GameResult:
    """players maps "A"/"B" to unstarted players."""
    began = time.monotonic()
    names = names or {"A": "A", "B": "B"}
    failed = start_players(players, "battleship", seed, "0 hits")
    if failed is not None:
        failed.duration_s = round(time.monotonic() - began, 2)
        return failed

    game = BattleshipGame(seed, config["board_size"], config["sonar_uses"], config["sonar_correct"], config["max_rounds"])
    clocks = TurnClocks(players, config["clock_s"], config["challenge_limit_s"])
    first = "A" if derive_seed(seed, "battleship-first") % 2 else "B"
    order = [first, other(first)]
    incidents, events, frames = [], [], []
    winner, reason = None, None

    def frame(text):
        frames.append({"a": game.boards["A"].grid(), "b": game.boards["B"].grid(), "text": text})

    def lose(side, failure):
        nonlocal winner, reason
        incidents.append(incident(side, failure))
        winner, reason = other(side), failure.kind

    try:
        placement_failures = {}
        for side in order:
            try:
                _ask_placement(game, clocks, side)
            except AgentFailure as failure:
                placement_failures[side] = failure
        if len(placement_failures) == 2:
            incidents.extend(incident(side, failure) for side, failure in placement_failures.items())
            reason = "both_agents_failed"
        elif placement_failures:
            side, failure = next(iter(placement_failures.items()))
            lose(side, failure)
        else:
            frame("Fleets placed")
            for round_number in range(1, game.max_rounds + 1):
                for side in order:
                    observation = game.observe(side, clocks)
                    try:
                        response = clocks.ask(side, observation)
                        event = game.apply_turn(side, response)
                    except AgentFailure as failure:
                        lose(side, failure)
                        rival = other(side)
                        try:
                            answer = clocks.ask(rival, game.observe(rival, clocks))
                            check_turn(answer, game.board_size, game.boards[rival].legal_moves(), game.boards[rival].sonar_left)
                        except AgentFailure as second:
                            incidents.append(incident(rival, second))
                            winner, reason = None, "both_agents_failed"
                        except ChallengeTimeUp:
                            pass
                        break
                    events.append(event)
                    what = f"sonar {event['center']} reads {event['reading']}" if "reading" in event else f"shot {event['target']}: {event['result']}"
                    frame(f"Turn {game.turn}, {names[side]}: {what}")
                    if live is not None:
                        live.update(
                            f"BATTLESHIP  round {round_number}/{game.max_rounds}\n"
                            f"{names['A']}: {game.score()['A']}  ({clocks.remaining['A']:.1f} s left)\n"
                            f"{names['B']}: {game.score()['B']}  ({clocks.remaining['B']:.1f} s left)"
                        )
                    if game.finished(side):
                        winner, reason = side, "fleet_destroyed"
                        break
                if reason is not None:
                    break
            else:
                winner, reason = game.adjudicate()
    except ChallengeTimeUp:
        winner, reason = game.adjudicate()
    finally:
        for player in players.values():
            player.stop()

    if live is not None:
        live.update(f"BATTLESHIP finished: {names['A']} {game.score()['A']} | {names['B']} {game.score()['B']}", force=True)
    return GameResult(
        game="battleship",
        winner=winner,
        reason=reason,
        score=game.score(),
        incidents=incidents,
        seed=seed,
        duration_s=round(time.monotonic() - began, 2),
        details={
            "first_player": first,
            "turns": game.turn,
            "events": events,
            "frames": frames,
            "clock_left_s": {side: round(clocks.remaining[side], 2) for side in SIDES},
        },
    )

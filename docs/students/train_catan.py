#!/usr/bin/env python3
"""Offline Q-learning trainer for games/catan/catan_agent.py.

Usage (from repo root):
    python docs/students/train_catan.py
    python docs/students/train_catan.py --games 3000 --out games/catan/q_table.json

Writes a JSON Q-table and a Python snippet line you can paste into catan_agent.py.
Trains on both sides; opponent is the heuristic baseline (with optional random mix).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from games.catan import catan_agent as agent
from games.catan.engine import (
    SIDE_OF,
    adjudicate,
    legal_actions,
    new_game,
    observation_for,
    victory_points,
)

ALPHA = 0.1
GAMMA = 0.9
EPS_START = 0.25
EPS_END = 0.05


def _key(obs, action):
    return f"{agent.state_features(obs)}|{action['type']}"


def _choose(obs, Q, eps, rng):
    actions = obs["actions"]
    if rng.random() < eps:
        return rng.choice(actions)["id"]
    return max(actions, key=lambda a: Q.get(_key(obs, a), 0.0))["id"]


def _heuristic(obs):
    return agent.heuristic_policy(obs)


def _random_policy(obs, rng):
    return rng.choice(obs["actions"])["id"]


def play_and_learn(Q, learner_side, seed, eps, rng, opponent="heuristic"):
    """One game. Updates Q for learner_side decisions. Returns winner, points."""
    game = new_game(seed, vps_to_win=7)
    last = {}  # side -> (features_key_action, vp)

    while game.winning_color() is None and game.state.num_turns // 2 < 100:
        actions = legal_actions(game)
        if len(actions) == 1:
            game.execute(actions[0])
            continue
        side = SIDE_OF[game.state.current_color()]
        obs = observation_for(game, side, actions, None, {"max_rounds": 100})
        vp = obs["me"]["victory_points"]

        if side == learner_side and side in last:
            prev_key, prev_vp = last[side]
            reward = vp - prev_vp
            best_next = max((Q.get(_key(obs, a), 0.0) for a in obs["actions"]), default=0.0)
            Q[prev_key] = agent.q_update(Q.get(prev_key, 0.0), reward, best_next, ALPHA, GAMMA)

        if side == learner_side:
            action_id = _choose(obs, Q, eps, rng)
            action = next(a for a in obs["actions"] if a["id"] == action_id)
            last[side] = (_key(obs, action), vp)
        else:
            if opponent == "random":
                action_id = _random_policy(obs, rng)
            else:
                action_id = _heuristic(obs)

        game.execute(actions[action_id])

    champ = game.winning_color()
    winner = SIDE_OF[champ] if champ is not None else adjudicate(game)[0]
    points = victory_points(game)

    # Terminal update for the learner's last decision
    if learner_side in last:
        prev_key, prev_vp = last[learner_side]
        final_vp = points[learner_side]
        reward = final_vp - prev_vp
        if winner == learner_side:
            reward += 1.0
        elif winner is not None:
            reward -= 1.0
        Q[prev_key] = agent.q_update(Q.get(prev_key, 0.0), reward, 0.0, ALPHA, GAMMA)

    return winner, points


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", type=Path, default=ROOT / "games/catan/q_table.json")
    parser.add_argument("--snippet", type=Path, default=ROOT / "games/catan/q_table_snippet.py")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    Q = dict(agent.Q)  # continue from any existing table
    wins = {"A": 0, "B": 0, None: 0}
    t0 = time.time()

    for i in range(args.games):
        frac = i / max(args.games - 1, 1)
        eps = EPS_START + (EPS_END - EPS_START) * frac
        seed = args.seed + i
        learner_side = "A" if i % 2 == 0 else "B"
        # Mostly train against heuristic; sprinkle random for coverage
        opponent = "random" if i % 10 == 0 else "heuristic"
        winner, _ = play_and_learn(Q, learner_side, seed, eps, rng, opponent=opponent)
        wins[winner] += 1
        if (i + 1) % 500 == 0 or i + 1 == args.games:
            elapsed = time.time() - t0
            print(
                f"[{i+1}/{args.games}] keys={len(Q)} wins={wins} "
                f"eps={eps:.3f} {elapsed:.1f}s",
                flush=True,
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Round for smaller files
    compact = {k: round(v, 5) for k, v in sorted(Q.items(), key=lambda kv: -abs(kv[1]))}
    args.out.write_text(json.dumps(compact))
    args.snippet.write_text(f"Q = {compact!r}\n")
    print(f"Wrote {args.out} ({len(compact)} keys)")
    print(f"Wrote {args.snippet}")


if __name__ == "__main__":
    main()

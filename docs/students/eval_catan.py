#!/usr/bin/env python3
"""Held-out evaluation for the Catan agent.

Usage (from repo root):
    python docs/students/eval_catan.py
    python docs/students/eval_catan.py --games 500 --start-seed 100000

Compares heuristic-only vs H+Q (act) on seeds outside the training range.
Writes docs/students/CATAN_EVAL.md with the numbers.
"""
from __future__ import annotations

import argparse
import importlib
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
)


def play(policy_a, policy_b, seed):
    game = new_game(seed, vps_to_win=7)
    policies = {"A": policy_a, "B": policy_b}
    while game.winning_color() is None and game.state.num_turns // 2 < 100:
        actions = legal_actions(game)
        if len(actions) == 1:
            game.execute(actions[0])
            continue
        side = SIDE_OF[game.state.current_color()]
        obs = observation_for(game, side, actions, None, {"max_rounds": 100})
        game.execute(actions[policies[side](obs)])
    champ = game.winning_color()
    return SIDE_OF[champ] if champ is not None else adjudicate(game)[0]


def matchup(name_a, policy_a, name_b, policy_b, seeds):
    wins = {name_a: 0, name_b: 0, "draw": 0}
    for seed in seeds:
        # Each seed twice: swap sides
        for a, b, pa, pb in (
            (name_a, name_b, policy_a, policy_b),
            (name_b, name_a, policy_b, policy_a),
        ):
            winner = play(pa, pb, seed)
            if winner == "A":
                wins[a] += 1
            elif winner == "B":
                wins[b] += 1
            else:
                wins["draw"] += 1
    return wins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=500, help="seeds (each played both sides)")
    parser.add_argument("--start-seed", type=int, default=100000)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/students/CATAN_EVAL.md")
    args = parser.parse_args()

    importlib.reload(agent)
    seeds = list(range(args.start_seed, args.start_seed + args.games))
    rng = random.Random(0)

    def heuristic(obs):
        return agent.heuristic_policy(obs)

    def hq(obs):
        return agent.act(obs)["action"]

    def rand(obs):
        return rng.choice(obs["actions"])["id"]

    t0 = time.time()
    print(f"Evaluating {args.games} seeds (x2 sides)...", flush=True)

    h_vs_rand = matchup("H", heuristic, "random", rand, seeds)
    print("H vs random:", h_vs_rand, flush=True)

    hq_vs_h = matchup("H+Q", hq, "H", heuristic, seeds)
    print("H+Q vs H:", hq_vs_h, flush=True)

    elapsed = time.time() - t0
    total_hq = hq_vs_h["H+Q"] + hq_vs_h["H"] + hq_vs_h["draw"]
    hq_rate = hq_vs_h["H+Q"] / total_hq if total_hq else 0
    prefer_q = hq_vs_h["H+Q"] > hq_vs_h["H"]

    report = f"""# Catan evaluation results

Held-out seeds `{args.start_seed}` … `{args.start_seed + args.games - 1}` (each played both sides).
Training used seeds starting at 1 for 3000 games, so this range does not overlap.

## H vs random

| | Wins |
|---|---|
| Heuristic (H) | {h_vs_rand['H']} |
| Random | {h_vs_rand['random']} |
| Draw | {h_vs_rand['draw']} |

## H+Q (`act`) vs H (`heuristic_policy`)

| | Wins |
|---|---|
| H+Q | {hq_vs_h['H+Q']} |
| H | {hq_vs_h['H']} |
| Draw | {hq_vs_h['draw']} |

H+Q win rate: **{hq_rate:.1%}** over {total_hq} games in {elapsed:.1f}s.

## Tournament default

{"`USE_Q = True` — H+Q won the held-out matchup." if prefer_q else "`USE_Q = False` — heuristic alone won the held-out matchup; Q values stay for `action_value` / the write-up."}
"""
    args.out.write_text(report)
    print(report)
    print(f"Wrote {args.out}")

    # Update USE_Q in the agent to match the evidence
    path = ROOT / "games/catan/catan_agent.py"
    text = path.read_text()
    new_flag = f"USE_Q = {prefer_q}"
    import re
    updated, n = re.subn(r"^USE_Q = (True|False)$", new_flag, text, count=1, flags=re.M)
    if n != 1:
        raise SystemExit(f"could not update USE_Q (replacements={n})")
    path.write_text(updated)
    print(f"Set {new_flag} in catan_agent.py")


if __name__ == "__main__":
    main()

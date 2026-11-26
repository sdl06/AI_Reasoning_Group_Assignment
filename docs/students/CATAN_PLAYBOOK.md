# Catan playbook: start to finish

Easy entry point for building `catan_agent.py`. Follow the steps in order. Official rules stay in [games/catan/README.md](../../games/catan/README.md); offline training API is in [TRAINING.md](TRAINING.md); graded functions are in [ASSIGNMENT.md](ASSIGNMENT.md).

---

## Step 0 — Our process (read this first)

**Goal.** Pass the automatic checks, beat a strong hand-written baseline in a fair eval, and ship one file that stays legal under the 5-second clock.

**Strategy we use.** Two layers, measured against each other:

| Layer | Role | Used where |
|---|---|---|
| **Heuristic baseline** | Explicit priorities + node scoring (planning / preconditions) | `heuristic_policy`, fallback in `act` |
| **Tabular Q-learning** | Values over a *small* state abstraction | `state_features`, `action_value`, `q_update`; optional guide for `act` |

We train **offline** for thousands of games, paste the `Q` table into `catan_agent.py`, and **do not learn during the match**. At the end we keep whichever policy wins on held-out seeds (heuristic alone vs Q-guided). A worse table than the baseline is still acceptable for the write-up if we report the numbers honestly.

**Why not deep search / MCTS first.** Decision budget is 5 seconds total for the whole game. A coarse Q-table + a sharp heuristic is safer and matches the course’s MDP / RL requirements.

**Workflow.**

```text
read samples → implement required stubs → strong heuristic
    → design tiny state_features → train Q offline (both sides)
    → embed Q → wire act → evaluate ≥500 seeds → ship winner + README
```

**File layout we aim for.**

```text
student_templates/catan_agent.py   # start from this
docs/students/train_catan.py       # optional local trainer (or a Colab cell)
# inside catan_agent.py after training:
#   Q = { "...features...|BUILD_CITY": 0.81, ... }
```

**Success criteria.**

1. `check_requirements("catan_agent.py")` passes all four Catan checks.
2. Agent never returns an illegal id, never throws, never blows the clock.
3. Eval: ≥500 seeds not used in training; report win rate vs demo / vs own baseline.
4. Technical README: baseline vs improved, features, rewards, planning, what we infer from `log`.

---

## Step 1 — Read the interface (30 minutes)

1. Skim [CHALLENGES.md](CHALLENGES.md) (Catan section) and [games/catan/README.md](../../games/catan/README.md).
2. Open the sample observations and note the real keys (misspelt keys fail silently):
   - `sample_observations/catan_initial_placement.json`
   - `sample_observations/catan_play_turn.json`
   - `sample_observations/catan_move_robber.json`
3. Copy `student_templates/catan_agent.py` into your team folder as `catan_agent.py`.
4. Confirm phases: `initial_placement`, `play_turn`, `move_robber`, `free_roads`.
5. Confirm reply shape: `return {"action": <id>}` where `id` is in `observation["actions"]`.

**Checkpoint.** You can explain what `me` vs `opponent` exposes (you never see their hand).

---

## Step 2 — Pass the required functions (skeleton)

Implement the four fixed names so checks go green early. Correct first; strong later.

### `q_update`

```python
def q_update(q, reward, best_next_q, alpha, gamma):
    return q + alpha * (reward + gamma * best_next_q - q)
```

### `state_features` (v1 — keep it tiny)

Deterministic list/tuple. Same observation → same features; different situations should differ. Example buckets:

- `phase`
- my VP bucket: `0–2 / 3–4 / 5–6 / 7+`
- opponent *visible* VP bucket (same cuts)
- flags: can build city / settlement / road / buy_dev (from legal action types)
- resource shape: `road_heavy` (wood+brick) / `city_heavy` (wheat+ore) / `mixed`
- hand-size bucket: `0–3 / 4–7 / 8+` (robber risk)

Too many features → empty Q-table forever. Prefer coarseness.

### `action_value`

Look up `Q[f"{state_features(obs)}|{action_type}"]`, else `0.0`. Key by **action type**, not raw id (ids change every decision).

### `heuristic_policy`

Always return a legal id. Start from `examples/team_demo_A/catan_agent.py` priorities, then tighten in Step 3.

**Checkpoint.**

```python
check_requirements("catan_agent.py")
```

---

## Step 3 — Make the baseline actually good

This is usually most of your strength. Improve `heuristic_policy` (and use it from `act` until Q is ready).

### Initial placement

- Score each legal settlement node: pip sum on adjacent tiles + resource diversity + port access.
- Prefer 6/8/5/9 numbers; avoid desert / robber-heavy clusters when possible.
- Second placement: fill missing resources (if first was wood/brick-heavy, hunt wheat/ore/sheep).
- Roads: point toward the next high-value empty node.

### Play turn (priority with intent)

1. `BUILD_CITY` (best VP / cost late game)
2. `BUILD_SETTLEMENT` (on highest production empty node you can reach)
3. Play useful dev cards (`KNIGHT` if large army / robber; `YEAR_OF_PLENTY` / `MONOPOLY` when they unlock a build; VP cards are automatic value)
4. `BUY_DEVELOPMENT_CARD` when city path is blocked but sheep/wheat/ore are rich
5. `BUILD_ROAD` only toward a settlement spot or longest-road contention
6. `MARITIME_TRADE` only if the trade **unlocks a build this turn**
7. `ROLL` / `END_TURN` when nothing productive remains

### Robber

- Prefer tiles that steal from opponent (`steal_from == "opponent"`).
- Prefer opponent’s highest pip tiles; avoid blocking yourself unless you are far ahead.

### Planning write-up hooks

For each build/trade you consider, state **preconditions** (resources, road connectivity, empty node) and **effects** (+1 VP, new production, unlock city). That satisfies the classical-planning explanation.

**Checkpoint.** Play 100+ games vs `demo` / random; baseline should clearly beat random.

---

## Step 4 — Infer what you can from the public log

Required explanation topic: logic / certainty.

From `observation["log"]` you can track (without guessing private cards beyond evidence):

- Opponent builds → they spent those resources (subtract from a running estimate).
- Dice rolls → expected payouts to settlements/cities you see.
- `BUY_DEVELOPMENT_CARD` by opponent → unknown card (+1 hidden); do not assume which.
- Discards → they had >7 cards; you see count, not composition (unless you discarded).
- Robber steals → if you were stolen from, you know the card; if they were, you only know they lost one.

Use estimates for **robber target** and **MONOPOLY** resource choice. Never invent certainty you do not have.

---

## Step 5 — Train tabular Q-learning offline

Use [TRAINING.md](TRAINING.md)’s `play_one_game` so observations and action ids match the judge.

### Loop (one decision of the learner)

1. `s = state_features(obs)`
2. ε-greedy over legal actions using `Q[s|type]` (explore with ε ≈ 0.1–0.2 early).
3. Execute; on the learner’s next decision (or game end), reward:
   - intermediate: `Δ me["victory_points"]`
   - terminal: `+1` win / `0` draw / `-1` loss (optionally scale)
4. `Q[s,a] = q_update(Q[s,a], r, max_{a'} Q[s',a'], α, γ)` with e.g. `α=0.1`, `γ=0.9`.

### Volume and sides

- Train on **thousands** of games (start with 2k–5k; grow if the table is still sparse).
- Seed picks who starts → average over many seeds **or** swap learner A/B each seed.
- Only update Q on the **learner’s** decisions; the opponent is part of the environment.
- Opponent for training: your heuristic first (learns to beat a strong policy); mix in random for coverage.

### Dump the table into the agent

```python
with open("q_table_line.py", "w") as f:
    f.write(f"Q = {Q!r}\n")
```

Copy that `Q = {...}` into `catan_agent.py`. Keep the same `state_features` in training and in the agent. A few hundred KB is fine if import stays under the load limit.

**Checkpoint.** Spot-check: common keys like `BUILD_CITY` when `can_city` should have higher value than `END_TURN` in the same state.

---

## Step 6 — Wire `act` (compete with the better policy)

Recommended play policy:

1. If `time_remaining_s` is low (treat `None` as “training / unlimited”), prefer the fast heuristic.
2. Otherwise score each legal action with `action_value`; break ties with the heuristic ranking.
3. If the Q key is missing, use `heuristic_policy` only.
4. Never call `catanatron.players` or train online.

Compare three variants on the same seeds:

| Variant | Description |
|---|---|
| H | `heuristic_policy` only |
| Q | pure argmax `action_value` |
| H+Q | Q with heuristic tie-break / fallback (usually best) |

**Checkpoint.** `run_game("catan", "catan_agent.py", opponent="demo")` works; no exceptions in logs.

---

## Step 7 — Evaluate like the tournament cares

Catan is noisy. Do not trust 20 games.

1. Freeze code and `Q`.
2. Run **≥500** games on seeds **outside** the training set.
3. Play both sides (or rely on seed diversity).
4. Record win / draw / loss vs demo and vs your own H-only agent.
5. Keep the variant with the best held-out win rate as the tournament `act`.
6. Still keep the required functions real (even if `act` mostly uses H).

Optional stress: cap yourself mentally at ~50 ms/decision average so 5 s total is safe.

---

## Step 8 — Push strength further (best-engine upgrades)

Do these **in order**; re-evaluate after each change. One lever at a time.

1. **Smarter placement** — joint score for settlement+road; simulate “what does this open for cities?”
2. **Build toward 7 VP** — when on 5–6 VP, bias every trade/road to the fastest forced win; ignore long-term economy.
3. **Longest road / largest army** — track lengths and knight counts; contest only when the VP swing matters.
4. **Trade discipline** — reject bank trades that do not unlock a build or a knight this turn or next.
5. **Richer rewards for Q** — small shaping for settlements/cities built, penalty for ending turn with a build available (only if it helps held-out win rate).
6. **Slightly richer features** — e.g. “distance-to-settlement in {0,1,2+}”, “has_port”; stop when coverage collapses.
7. **Self-play** — once H+Q beats H, train another table against the current agent.
8. **Optional expectimax / short rollouts** — only for robber or 1-ply build choice when time_remaining_s is healthy; abort if clock is tight.
9. **Optional MCTS** — last resort; hard under 5 s unless severely capped (few sims, heuristic priors).

Stop when gains plateau on the 500-seed eval. Extra complexity that does not move win rate is not “better.”

---

## Step 9 — Package and explain

1. Single file `catan_agent.py` with `Q` embedded, no illegal imports.
2. Team `README.md` section for Catan using the template in [ASSIGNMENT.md](ASSIGNMENT.md):
   - problem formulation (states, actions, observation, objective)
   - algorithms and where they live in the file
   - baseline vs improved numbers (seeds, opponents, win rates)
   - clock behaviour
   - limits / what you would do next
3. Zip with the other three agents for the full match.

---

## Quick command cheat sheet

```python
# Practice one game
practice = run_game("catan", "catan_agent.py", opponent="demo")
show_game(practice)
print(practice["logs"]["A"])

# Graded stubs
check_requirements("catan_agent.py")

# Offline training entry (see TRAINING.md)
from games.catan.engine import new_game, legal_actions, observation_for, SIDE_OF, adjudicate, victory_points
```

---

## Anti-patterns (avoid)

- Huge feature vectors or continuous values as Q keys.
- Keying Q by action `id` instead of `type`.
- Training only as player A.
- Declaring a winner from <100 games.
- Importing `catanatron.players` into the submitted file.
- Learning during the match or downloading weights.
- Spending the clock on search before a solid heuristic exists.

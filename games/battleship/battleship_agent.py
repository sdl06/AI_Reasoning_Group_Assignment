"""Battleship agent. Team: <your team name>

Hunting uses a belief filter per enemy ship (three of them, one per guess of how often
the rival moves). Ships we have hit are found with constraint reasoning over placements.
See the Battleship section of README.md for the full explanation.
"""
import random

import numpy as np

DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}

# A placement through two or more open hits is much more likely than one through a single hit
LINE_BONUS = 25

# Only scan when no cell looks better than this for a shot
SONAR_THRESHOLD = 0.12
MIN_SONAR_GAIN = 0.3

TIME_MARGIN = 0.5

# Guesses for how often the rival moves a ship per turn: never, like demo_a, every turn
MOVE_RATES = [0.0, 0.25, 1.0]
RATE_PRIOR = [0.3, 0.4, 0.3]
MIN_WEIGHT = 0.02


def ship_cells(row, col, length, orientation):
    if orientation == "H":
        return [(row, col + k) for k in range(length)]
    return [(row + k, col) for k in range(length)]


def fits(row, col, length, orientation, n):
    if orientation == "H":
        return 0 <= row < n and 0 <= col and col + length <= n
    return 0 <= col < n and 0 <= row and row + length <= n


# Required functions

def consistent_placements(length, board_size, blocked, required):
    blocked = {tuple(c) for c in blocked}
    required = {tuple(c) for c in required}
    result = []
    for orientation in ("H", "V"):
        for row in range(board_size):
            for col in range(board_size):
                if not fits(row, col, length, orientation, board_size):
                    continue
                cells = set(ship_cells(row, col, length, orientation))
                if cells & blocked or not required <= cells:
                    continue
                result.append([row, col, orientation])
    return result


def reading_probability(reading, count, region_cells, correct_probability):
    side = (1 - correct_probability) / 2
    outcomes = {count: correct_probability, count - 1: side, count + 1: side}
    outcomes = {r: p for r, p in outcomes.items() if 0 <= r <= region_cells}
    return outcomes.get(reading, 0.0) / sum(outcomes.values())


def sonar_posterior(prior, reading, region_cells, correct_probability):
    posterior = {}
    for key, p in prior.items():
        posterior[key] = p * reading_probability(reading, int(key), region_cells, correct_probability)
    total = sum(posterior.values())
    if total == 0:
        return dict(prior)
    return {key: p / total for key, p in posterior.items()}


def predict_ship_belief(belief, length, orientation, move_probability):
    belief = np.array(belief, dtype=float)
    n = belief.shape[0]
    valid = np.zeros((n, n), dtype=bool)
    for row in range(n):
        for col in range(n):
            valid[row, col] = fits(row, col, length, orientation, n)
    return spread(belief, valid, move_probability).tolist()


# Transition model: with probability p the ship takes one step, picked uniformly
# among the directions that land on a valid top left cell. Otherwise it stays.

def spread(belief, valid, p):
    n = belief.shape[0]
    padded = np.zeros((n + 2, n + 2), dtype=bool)
    padded[1:n + 1, 1:n + 1] = valid

    options = []
    for dr, dc in DIRECTIONS.values():
        can_go = padded[1 + dr:1 + dr + n, 1 + dc:1 + dc + n]
        options.append((dr, dc, can_go))
    n_options = sum(can_go.astype(int) for _, _, can_go in options)

    stuck = n_options == 0
    stays = np.where(stuck, belief, (1 - p) * belief)
    share = np.where(stuck, 0.0, p * belief / np.maximum(n_options, 1))

    arrivals = np.zeros((n + 2, n + 2))
    for dr, dc, can_go in options:
        arrivals[1 + dr:1 + dr + n, 1 + dc:1 + dc + n] += share * can_go
    return stays + arrivals[1:n + 1, 1:n + 1]


# Belief about the rival's fleet
#
# A belief for one ship is an array (2, n, n): the probability that its top left cell is
# [row, col], horizontal in index 0 and vertical in index 1. Ships are treated as independent.
# We do not know how often the rival moves, so we keep one set of beliefs per guess
# (MOVE_RATES) and weight each guess by how well it predicted what our shots found.


class Filter:
    def __init__(self, rate, weight, beliefs):
        self.rate = rate
        self.weight = weight
        self.beliefs = beliefs

    def normalise(self, i, model):
        total = self.beliefs[i].sum()
        if total <= 0:
            # the evidence contradicts this guess, so start the ship again
            valid = model.valid_mask(model.lengths[i])
            self.beliefs[i] = valid / max(valid.sum(), 1)
        else:
            self.beliefs[i] = self.beliefs[i] / total

    def advance(self, model, steps):
        # only one ship moves per turn, so the rate is shared between the ships that can move
        p = min(1.0, self.rate / model.moving_ships())
        if p == 0:
            return
        for _ in range(steps):
            for i, length in enumerate(model.lengths):
                valid = model.valid_mask(length)
                b = self.beliefs[i]
                for o in range(2):
                    b[o] = spread(b[o], valid[o] > 0, p) * valid[o]
                self.normalise(i, model)

    def occupancy(self, model):
        n = model.n
        free = np.ones((n, n))
        for i, length in enumerate(model.lengths):
            b = self.beliefs[i]
            cover = np.zeros((n, n))
            for k in range(length):
                cover[:, k:] += b[0][:, :n - k]
                cover[k:, :] += b[1][:n - k, :]
            free *= 1 - np.clip(cover, 0, 1)
        return 1 - free

    def count_distributions(self, model, center):
        per_ship = []
        for i, length in enumerate(model.lengths):
            counts = model.window_counts(center, length)
            dist = np.array([self.beliefs[i][counts == k].sum() for k in range(length + 1)])
            per_ship.append((counts, dist))
        return per_ship

    def count_prior(self, per_ship):
        total = np.array([1.0])
        for _, dist in per_ship:
            total = np.convolve(total, dist)
        return total

    def apply_sonar(self, model, center, reading, q):
        cells, known = model.window_size(center)
        per_ship = self.count_distributions(model, center)

        # how likely this reading was under this guess, before updating
        count_prior = self.count_prior(per_ship)
        predicted = sum(p * reading_probability(reading, known + m, cells, q)
                        for m, p in enumerate(count_prior) if known + m <= cells)

        for i in range(len(model.lengths)):
            others = self.count_prior([s for j, s in enumerate(per_ship) if j != i])
            counts, dist = per_ship[i]
            likelihood = np.zeros(len(dist))
            for k in range(len(dist)):
                for m, p_m in enumerate(others):
                    if known + k + m <= cells:
                        likelihood[k] += p_m * reading_probability(reading, known + k + m, cells, q)
            self.beliefs[i] = self.beliefs[i] * likelihood[counts]
            self.normalise(i, model)
        return predicted


class EnemyModel:
    def __init__(self, n, lengths):
        self.n = n
        self.lengths = sorted(lengths, reverse=True)
        self.damaged = {}        # cell: turn it was first hit
        self.sunk_cells = set()
        self.last_miss = {}      # cell: last turn a plain miss landed there
        self.time = 0
        self.masks = {}
        self.filters = []
        for rate, weight in zip(MOVE_RATES, RATE_PRIOR):
            beliefs = []
            for length in self.lengths:
                valid = self.valid_mask(length)
                beliefs.append(valid / valid.sum())
            self.filters.append(Filter(rate, weight, beliefs))

    def valid_mask(self, length):
        """Placements on the board that do not cover a damaged cell. A ship that can still
        move has never been hit, and it cannot sit on top of another ship's damage."""
        key = (length, len(self.damaged))
        if key not in self.masks:
            n = self.n
            mask = np.zeros((2, n, n))
            for o, orientation in enumerate("HV"):
                for row in range(n):
                    for col in range(n):
                        if not fits(row, col, length, orientation, n):
                            continue
                        cells = ship_cells(row, col, length, orientation)
                        if not any(c in self.damaged for c in cells):
                            mask[o, row, col] = 1
            self.masks[key] = mask
        return self.masks[key]

    def covering(self, cell, length):
        """Top left positions whose ship would cover this cell."""
        n = self.n
        r, c = cell
        mask = np.zeros((2, n, n))
        for k in range(length):
            if fits(r, c - k, length, "H", n):
                mask[0, r, c - k] = 1
            if fits(r - k, c, length, "V", n):
                mask[1, r - k, c] = 1
        return mask

    def open_hits(self):
        return [c for c in self.damaged if c not in self.sunk_cells]

    def moving_ships(self):
        hit_but_floating = 1 if self.open_hits() else 0
        return max(1, len(self.lengths) - hit_but_floating)

    def reweight(self, likelihoods):
        for f, lik in zip(self.filters, likelihoods):
            f.weight *= max(lik, 1e-6)
        total = sum(f.weight for f in self.filters)
        for f in self.filters:
            # keep every guess alive in case the rival changes how it plays
            f.weight = max(f.weight / total, MIN_WEIGHT)
        total = sum(f.weight for f in self.filters)
        for f in self.filters:
            f.weight /= total

    # filtering: predict

    def advance(self, steps):
        if steps > 0:
            for f in self.filters:
                f.advance(self, steps)

    # filtering: update with what our shots and scans told us

    def apply_shot(self, shot):
        cell = tuple(shot["target"])
        result = shot["result"]
        if result == "MISS" and shot.get("already_damaged"):
            return

        # only hunting shots say much about the moving ships, target shots aim at a ship
        # that has already stopped
        if not self.open_hits():
            occ = [f.occupancy(self)[cell] for f in self.filters]
            self.reweight([1 - o if result == "MISS" else o for o in occ])

        if result == "MISS":
            self.last_miss[cell] = shot["turn"]
            for f in self.filters:
                for i, length in enumerate(self.lengths):
                    f.beliefs[i] *= 1 - self.covering(cell, length)
                    f.normalise(i, self)
            return

        self.damaged[cell] = shot["turn"]
        if result == "SUNK":
            self.mark_sunk(cell, shot["sunk_length"])
        for f in self.filters:
            for i, length in enumerate(self.lengths):
                f.beliefs[i] *= self.valid_mask(length)
                f.normalise(i, self)

    def apply_sonar(self, scan, q):
        center = tuple(scan["center"])
        predicted = [f.apply_sonar(self, center, scan["reading"], q) for f in self.filters]
        self.reweight(predicted)

    def mark_sunk(self, cell, length):
        n = self.n
        candidates = []
        for orientation in "HV":
            for k in range(length):
                r, c = (cell[0], cell[1] - k) if orientation == "H" else (cell[0] - k, cell[1])
                if not fits(r, c, length, orientation, n):
                    continue
                cells = ship_cells(r, c, length, orientation)
                if all(x in self.damaged and x not in self.sunk_cells for x in cells):
                    candidates.append(cells)
        if candidates:
            # if more than one line works, the most recent hits are the likeliest
            best = max(candidates, key=lambda cells: sum(self.damaged[x] for x in cells))
            self.sunk_cells.update(best)
        else:
            self.sunk_cells.add(cell)

        if length in self.lengths:
            i = self.lengths.index(length)
            del self.lengths[i]
            for f in self.filters:
                del f.beliefs[i]

    # sonar helpers

    def window_size(self, center):
        n = self.n
        r0, r1 = max(0, center[0] - 1), min(n - 1, center[0] + 1)
        c0, c1 = max(0, center[1] - 1), min(n - 1, center[1] + 1)
        cells = (r1 - r0 + 1) * (c1 - c0 + 1)
        known = sum(1 for (r, c) in self.damaged if r0 <= r <= r1 and c0 <= c <= c1)
        return cells, known

    def window_counts(self, center, length):
        """For every placement, how many of its cells fall in the 3x3 window."""
        n = self.n
        window = np.zeros((n + length, n + length))
        r0, r1 = max(0, center[0] - 1), min(n - 1, center[0] + 1)
        c0, c1 = max(0, center[1] - 1), min(n - 1, center[1] + 1)
        window[r0:r1 + 1, c0:c1 + 1] = 1
        counts = np.zeros((2, n, n))
        for k in range(length):
            counts[0] += window[:n, k:k + n]
            counts[1] += window[k:k + n, :n]
        return counts.astype(int)

    def sonar_gain(self, center, q):
        """Mutual information between the true count and the reading, in bits."""
        cells, known = self.window_size(center)
        count_dist = np.zeros(sum(self.lengths) + 1)
        for f in self.filters:
            dist = f.count_prior(f.count_distributions(self, center))
            count_dist[:len(dist)] += f.weight * dist

        reading_dist = np.zeros(cells + 1)
        noise = 0.0
        for m, p_m in enumerate(count_dist):
            if p_m <= 0 or known + m > cells:
                continue
            probs = np.array([reading_probability(r, known + m, cells, q) for r in range(cells + 1)])
            reading_dist += p_m * probs
            nz = probs[probs > 0]
            noise -= p_m * (nz * np.log2(nz)).sum()
        nz = reading_dist[reading_dist > 0]
        return -(nz * np.log2(nz)).sum() - noise

    # choosing a cell

    def occupancy(self):
        occ = sum(f.weight * f.occupancy(self) for f in self.filters)
        for cell in self.damaged:
            occ[cell] = 0
        return occ

    def target_scores(self):
        open_hits = set(self.open_hits())
        scores = np.zeros((self.n, self.n))
        for length in set(self.lengths):
            copies = self.lengths.count(length)
            seen = set()
            for hit in open_hits:
                for row, col, orientation in consistent_placements(length, self.n, self.sunk_cells, [hit]):
                    if (row, col, orientation) in seen:
                        continue
                    seen.add((row, col, orientation))
                    cells = ship_cells(row, col, length, orientation)
                    covered = [c for c in cells if c in open_hits]
                    hit_since = min(self.damaged[c] for c in covered)
                    # the ship stopped moving when it was first hit, so later misses rule it out
                    if any(self.last_miss.get(c, -1) > hit_since for c in cells):
                        continue
                    weight = copies * LINE_BONUS ** (len(covered) - 1)
                    for c in cells:
                        if c not in self.damaged:
                            scores[c] += weight
        return scores


def best_cell(scores):
    top = scores.max()
    options = list(zip(*np.where(scores >= top - 1e-12)))
    r, c = random.choice(options)
    return [int(r), int(c)]


# Our own fleet

def place_fleet(fleet, n):
    for _ in range(500):
        taken = set()
        placements = []
        for ship in sorted(fleet, key=lambda s: -s["length"]):
            spot = None
            for _ in range(100):
                orientation = random.choice("HV")
                row, col = random.randrange(n), random.randrange(n)
                if not fits(row, col, ship["length"], orientation, n):
                    continue
                cells = ship_cells(row, col, ship["length"], orientation)
                # leave a gap so a hit on one ship does not lead the rival onto the next
                around = {(r + dr, c + dc) for r, c in cells for dr in (-1, 0, 1) for dc in (-1, 0, 1)}
                if around & taken:
                    continue
                spot = (row, col, orientation, cells)
                break
            if spot is None:
                break
            row, col, orientation, cells = spot
            taken.update(cells)
            placements.append({"ship": ship["ship"], "row": row, "col": col, "orientation": orientation})
        if len(placements) == len(fleet):
            return placements
    return None


def danger_map(observation):
    """Where the rival is most likely to shoot next: around hits on ships it has not sunk."""
    n = observation["board_size"]
    danger = np.zeros((n, n))
    for ship in observation["my_ships"]:
        if not ship["damaged_cells"]:
            continue
        weight = 1 if ship["sunk"] else 4
        for r, c in ship["damaged_cells"]:
            for dr, dc in DIRECTIONS.values():
                for step, w in ((1, weight), (2, weight / 2)):
                    rr, cc = r + dr * step, c + dc * step
                    if 0 <= rr < n and 0 <= cc < n:
                        danger[rr, cc] += w
    return danger


def choose_move(observation):
    legal = observation.get("legal_moves") or []
    if not legal:
        return None
    danger = danger_map(observation)
    ships = {s["ship"]: s for s in observation["my_ships"]}

    best, best_delta = [], None
    for move in legal:
        cells = [tuple(c) for c in ships[move["ship"]]["cells"]]
        dr, dc = DIRECTIONS[move["direction"]]
        before = sum(danger[c] for c in cells)
        after = sum(danger[r + dr, c + dc] for r, c in cells)
        delta = after - before
        if best_delta is None or delta < best_delta - 1e-9:
            best, best_delta = [move], delta
        elif abs(delta - best_delta) < 1e-9:
            best.append(move)
    if best_delta > 0:
        return None
    # moving even when nothing is at risk keeps the rival's old misses out of date
    move = random.choice(best)
    return {"ship": move["ship"], "direction": move["direction"]}


# Decision function

model = None


def act(observation):
    try:
        return decide(observation)
    except Exception as error:
        # an exception loses the game, a plain shot does not
        print("fallback:", repr(error))
        if observation["phase"] == "placement":
            return {"placements": None}
        n = observation["board_size"]
        return {"shot": [random.randrange(n), random.randrange(n)]}


def decide(observation):
    global model
    n = observation["board_size"]

    if observation["phase"] == "placement":
        model = None
        return {"placements": place_fleet(observation["fleet"], n)}

    if model is None or observation["turn"] < model.time:
        model = EnemyModel(n, [s["length"] for s in observation["my_ships"]])

    q = observation.get("sonar_correct_probability", 0.8)
    events = [("shot", s) for s in observation["my_shots"]]
    events += [("sonar", s) for s in observation["my_sonar"]]
    events.sort(key=lambda e: e[1]["turn"])
    for kind, event in events:
        if event["turn"] <= model.time:
            continue
        model.advance(event["turn"] - model.time - 1)
        if kind == "shot":
            model.apply_shot(event)
        else:
            model.apply_sonar(event, q)
        model.time = event["turn"]
    model.advance(observation["turn"] - model.time)
    model.time = observation["turn"]

    answer = {}
    move = choose_move(observation)
    if move is not None:
        answer["move"] = move

    if model.open_hits():
        scores = model.target_scores()
        if scores.max() > 0:
            answer["shot"] = best_cell(scores)
            return answer

    occ = model.occupancy()
    time_left = observation.get("time_remaining_s")
    has_time = time_left is None or time_left > TIME_MARGIN + 0.5
    if observation.get("sonar_remaining", 0) > 0 and occ.max() < SONAR_THRESHOLD and has_time:
        gains = {(r, c): model.sonar_gain((r, c), q) for r in range(1, n - 1) for c in range(1, n - 1)}
        center = max(gains, key=gains.get)
        if gains[center] > MIN_SONAR_GAIN:
            answer["sonar"] = [int(center[0]), int(center[1])]
            return answer

    answer["shot"] = best_cell(occ)
    return answer

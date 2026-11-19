"""A move-by-move replay of each game, opening on its final position, and the move list."""
from __future__ import annotations

import html
import json
import uuid

import chess

from tournament.results import ending_words


def replay_html(moves: list, title: str) -> str:
    """A self-contained step-through of one game, with no external files."""
    board = chess.Board()
    fens = [board.board_fen()]
    sans = []
    for uci in moves:
        move = chess.Move.from_uci(uci)
        sans.append(board.san(move))
        board.push(move)
        fens.append(board.board_fen())
    element = "replay_" + uuid.uuid4().hex[:8]
    pieces = dict(zip("KQRBNPkqrbnp", "♔♕♖♗♘♙♚♛♜♝♞♟"))
    return f"""
<div id="{element}" style="font-family:sans-serif">
  <b>{html.escape(title)}</b>
  <div class="grid" style="display:grid;grid-template-columns:repeat(8,34px);grid-auto-rows:34px;width:272px;margin:6px 0"></div>
  <button class="first">|&lt;</button> <button class="prev">&lt;</button>
  <button class="next">&gt;</button> <button class="last">&gt;|</button>
  <span class="label" style="margin-left:8px"></span>
</div>
<script>
(function() {{
  const root = document.getElementById("{element}");
  const fens = {json.dumps(fens)};
  const moves = {json.dumps(moves)};
  const sans = {json.dumps(sans)};
  const glyph = {json.dumps(pieces, ensure_ascii=False)};
  let at = fens.length - 1;
  function draw() {{
    let cells = "";
    fens[at].split("/").forEach((row, r) => {{
      let c = 0;
      for (const ch of row) {{
        const n = parseInt(ch);
        for (let i = 0; i < (isNaN(n) ? 1 : n); i++) {{
          const dark = (r + c) % 2 === 1;
          cells += `<div style="display:flex;align-items:center;justify-content:center;font-size:26px;line-height:1;background:${{dark ? "#b58863" : "#f0d9b5"}};color:#111">${{isNaN(n) ? glyph[ch] : ""}}</div>`;
          c++;
        }}
      }}
    }});
    root.querySelector(".grid").innerHTML = cells;
    root.querySelector(".label").textContent = at === 0 ? "Start position" : `Move ${{Math.ceil(at / 2)}}, ${{at % 2 ? "white" : "black"}}: ${{sans[at - 1]}} (${{moves[at - 1]}})`;
  }}
  root.querySelector(".first").onclick = () => {{ at = 0; draw(); }};
  root.querySelector(".prev").onclick = () => {{ at = Math.max(0, at - 1); draw(); }};
  root.querySelector(".next").onclick = () => {{ at = Math.min(fens.length - 1, at + 1); draw(); }};
  root.querySelector(".last").onclick = () => {{ at = fens.length - 1; draw(); }};
  draw();
}})();
</script>"""


def san_moves(moves: list) -> str:
    board = chess.Board()
    return board.variation_san([chess.Move.from_uci(uci) for uci in moves]) if moves else "(no moves)"


def show(result: dict, names: dict) -> None:
    from IPython.display import HTML, display

    for number, game in enumerate(result["details"]["games"], 1):
        white, black = names[game["white"]], names["B" if game["white"] == "A" else "A"]
        winner = names[game["winner"]] if game["winner"] else "draw"
        heading = f"Game {number}: {white} (white) vs {black} (black). Result: {winner} ({ending_words(game['reason'])})"
        display(HTML(f"<h4>{html.escape(heading)}</h4>"))
        if game["moves"]:
            display(HTML(replay_html(game["moves"], "Replay")))
        display(HTML(f"<details><summary>All moves</summary><p style='font-family:monospace'>{html.escape(san_moves(game['moves']))}</p></details>"))

"""Replay of both boards, turn by turn, in one self-contained block."""
from __future__ import annotations

import html
import json
import uuid


def replay_html(frames: list, names: dict, board_size: int = 10) -> str:
    element = "bs_" + uuid.uuid4().hex[:8]
    return f"""
<div id="{element}" style="font-family:sans-serif">
  <div style="display:flex;gap:24px;flex-wrap:wrap">
    <div><b>{html.escape(names['A'])}</b><div class="a"></div></div>
    <div><b>{html.escape(names['B'])}</b><div class="b"></div></div>
  </div>
  <div style="margin-top:6px">
    <button class="first">|&lt;</button> <button class="prev">&lt;</button>
    <button class="next">&gt;</button> <button class="last">&gt;|</button>
    <span class="label" style="margin-left:8px"></span>
  </div>
</div>
<script>
(function() {{
  const root = document.getElementById("{element}");
  const frames = {json.dumps(frames)};
  const size = {board_size};
  const colors = {{".": "#cfe8f3", "S": "#5c6b73", "X": "#d1495b"}};
  let at = frames.length - 1;
  function grid(text) {{
    let out = "";
    for (let r = 0; r < size; r++) {{
      for (let c = 0; c < size; c++) {{
        out += `<span style="display:inline-block;width:20px;height:20px;margin:1px;background:${{colors[text[r * size + c]]}}"></span>`;
      }}
      out += "<br>";
    }}
    return `<div style="line-height:0">${{out}}</div>`;
  }}
  function draw() {{
    root.querySelector(".a").innerHTML = grid(frames[at].a);
    root.querySelector(".b").innerHTML = grid(frames[at].b);
    root.querySelector(".label").textContent = frames[at].text;
  }}
  root.querySelector(".first").onclick = () => {{ at = 0; draw(); }};
  root.querySelector(".prev").onclick = () => {{ at = Math.max(0, at - 1); draw(); }};
  root.querySelector(".next").onclick = () => {{ at = Math.min(frames.length - 1, at + 1); draw(); }};
  root.querySelector(".last").onclick = () => {{ at = frames.length - 1; draw(); }};
  draw();
}})();
</script>"""


def show(result: dict, names: dict) -> None:
    from IPython.display import HTML, display

    frames = result["details"].get("frames", [])
    if frames:
        display(HTML(f"<p>Grey: ship. Red: damaged segment. {result['details']['turns']} turns played.</p>"))
        display(HTML(replay_html(frames, names, int(len(frames[0]["a"]) ** 0.5))))

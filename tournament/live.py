"""Progress display that never touches an agent's clock."""
from __future__ import annotations

import html
import time


def in_notebook() -> bool:
    try:
        from IPython import get_ipython

        return get_ipython() is not None and hasattr(get_ipython(), "kernel")
    except ImportError:
        return False


class LiveView:
    """One block of text that keeps updating in place in a notebook."""

    def __init__(self, enabled: bool = True, min_interval_s: float = 0.5, console_interval_s: float = 10.0):
        self.enabled = enabled
        self.min_interval_s = min_interval_s
        self.console_interval_s = console_interval_s
        self._handle = None
        self._notebook = enabled and in_notebook()
        self._last = 0.0

    def update(self, text: str, force: bool = False) -> None:
        if not self.enabled:
            return
        now = time.monotonic()
        interval = self.min_interval_s if self._notebook else self.console_interval_s
        if not force and now - self._last < interval:
            return
        self._last = now
        if not self._notebook:
            print(text, flush=True)
            return
        from IPython.display import HTML, display

        content = HTML(f"<pre style='font-size:14px;line-height:1.35'>{html.escape(text)}</pre>")
        if self._handle is None:
            self._handle = display(content, display_id=True)
        else:
            self._handle.update(content)

"""Load tournament_config.json and apply overrides."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "tournament_config.json"


def _merge(base: dict, overrides: dict, path: str = "") -> dict:
    for key, value in overrides.items():
        if key not in base:
            options = ", ".join(sorted(base))
            raise ValueError(f"Unknown setting {path}{key}. The settings here are: {options}")
        if isinstance(value, dict) and isinstance(base[key], dict):
            _merge(base[key], value, f"{path}{key}.")
        else:
            base[key] = value
    return base


def load_config(overrides: dict = None) -> dict:
    """overrides example: {"chess": {"clock_s": 5}} changes only that value."""
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return _merge(config, copy.deepcopy(overrides)) if overrides else config

"""IE University AI Agent Tournament: the judge.

    from tournament import run_match, run_game, check_requirements, show_match
"""
import importlib

_EXPORTS = {
    "check_requirements": "academic_checks",
    "download_result": "results",
    "show_game": "results",
    "show_match": "results",
    "run_game": "runner",
    "run_match": "runner",
    "verify_environment": "setup_check",
    "TeamError": "teams",
    "list_teams": "teams",
    "load_team": "teams",
}

__all__ = sorted(_EXPORTS)


def __getattr__(name):
    # Imported on demand: the game engines themselves use tournament.agents and friends.
    if name not in _EXPORTS:
        raise AttributeError(name)
    return getattr(importlib.import_module(f".{_EXPORTS[name]}", __name__), name)

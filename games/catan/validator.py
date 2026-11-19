"""An agent answers with the id of one of the legal actions the judge just listed."""
from __future__ import annotations

from tournament.agents import ILLEGAL, MALFORMED, AgentFailure


def parse_action(response, number_of_actions: int) -> int:
    if not isinstance(response, dict) or "action" not in response:
        raise AgentFailure(MALFORMED, f'expected {{"action": <id>}}, got {response!r}'[:300])
    action = response["action"]
    if not isinstance(action, int) or isinstance(action, bool):
        raise AgentFailure(MALFORMED, f"action id must be an integer, got {action!r}"[:300])
    if not 0 <= action < number_of_actions:
        raise AgentFailure(ILLEGAL, f"action id {action} is not one of the {number_of_actions} legal actions")
    return action

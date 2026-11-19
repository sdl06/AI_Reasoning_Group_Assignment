"""Runs inside each agent's own process. Students never import this file.

It loads the student's .py once, keeps it alive, and talks to the judge with
JSON Lines over a private pipe. Anything the student prints goes to stderr, so
a stray print() can never corrupt the protocol.

Modes:
  turn    the judge sends observations, the agent's act() answers each one.
  stream  the judge sends one problem, the agent's solve() submits solutions.
  rpc     the judge calls named functions (used by the requirement checks).
"""
import importlib.util
import json
import os
import random
import sys
import threading
import traceback


def _limit_memory(limit_mb: int) -> None:
    """Hard ceiling on address space where the OS supports it (Linux does)."""
    try:
        import resource

        _, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (limit_mb * 2 * 1024 * 1024, hard))
    except Exception:
        pass


def _native(value):
    """Let agents answer with numpy integers and arrays."""
    if hasattr(value, "tolist"):
        return value.tolist()
    raise TypeError(f"{type(value).__name__} cannot be sent to the judge")


class Protocol:
    """The judge's private channel. Student code never receives a reference."""

    def __init__(self):
        self._out = os.fdopen(os.dup(1), "w", buffering=1, encoding="utf-8")
        self._in = os.fdopen(os.dup(0), "r", encoding="utf-8")
        os.dup2(2, 1)
        devnull = os.open(os.devnull, os.O_RDONLY)
        os.dup2(devnull, 0)
        os.close(devnull)
        self._lock = threading.Lock()

    def send(self, message: dict) -> None:
        line = json.dumps(message, default=_native)
        with self._lock:
            self._out.write(line + "\n")
            self._out.flush()

    def receive(self):
        line = self._in.readline()
        return json.loads(line) if line else None


def _load_module(path: str):
    directory = os.path.dirname(os.path.abspath(path))
    sys.path[0] = directory
    spec = importlib.util.spec_from_file_location("student_agent", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["student_agent"] = module
    spec.loader.exec_module(module)
    return module


def _serve_turns(protocol: Protocol, act) -> None:
    while True:
        message = protocol.receive()
        if message is None or message.get("type") == "shutdown":
            return
        try:
            response = act(message["observation"])
            json.dumps(response, default=_native)
        except Exception:
            protocol.send({"type": "error", "id": message["id"], "error": traceback.format_exc()})
            continue
        protocol.send({"type": "response", "id": message["id"], "response": response})


def _serve_stream(protocol: Protocol, solve) -> None:
    message = protocol.receive()
    if message is None:
        return

    def submit(path) -> None:
        """Send one complete route to the judge. Call it as often as you like."""
        protocol.send({"type": "solution", "path": path})

    try:
        solve(message["observation"], submit)
    except Exception:
        protocol.send({"type": "error", "error": traceback.format_exc()})
    else:
        protocol.send({"type": "done"})


def _serve_rpc(protocol: Protocol, module) -> None:
    while True:
        message = protocol.receive()
        if message is None or message.get("type") == "shutdown":
            return
        call = message["observation"]
        reply_id = message["id"]
        function = getattr(module, call["fn"], None)
        if not callable(function):
            protocol.send({"type": "response", "id": reply_id, "response": {"__missing__": True}})
            continue
        try:
            response = {"value": function(*call["args"])}
            json.dumps(response, default=_native)
        except NotImplementedError:
            response = {"__not_implemented__": True}
        except Exception:
            protocol.send({"type": "error", "id": reply_id, "error": traceback.format_exc()})
            continue
        protocol.send({"type": "response", "id": reply_id, "response": response})


def main() -> None:
    path, mode, seed, limit_mb = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    protocol = Protocol()
    _limit_memory(limit_mb)
    random.seed(seed)
    try:
        module = _load_module(path)
        entry = None
        if mode != "rpc":
            name, signature = ("act", "act(observation)") if mode == "turn" else ("solve", "solve(problem, submit)")
            entry = getattr(module, name, None)
            if not callable(entry):
                raise TypeError(f"Your file must define this function: def {signature}")
    except BaseException:
        protocol.send({"type": "load_error", "error": traceback.format_exc()})
        return
    protocol.send({"type": "ready"})
    if mode == "turn":
        _serve_turns(protocol, entry)
    elif mode == "stream":
        _serve_stream(protocol, entry)
    else:
        _serve_rpc(protocol, module)


if __name__ == "__main__":
    main()

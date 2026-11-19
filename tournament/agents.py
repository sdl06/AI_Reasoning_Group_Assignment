"""Run one student agent in its own process, with real limits the judge enforces.

The judge's clock is the only clock that counts. A hung, crashed or
memory-hungry agent loses that agent the game, and the notebook carries on.
"""
from __future__ import annotations

import ast
import collections
import json
import os
import queue
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

import psutil

HOST_SCRIPT = Path(__file__).with_name("agent_host.py")
MAX_LINE_BYTES = 4 * 1024 * 1024
STDERR_TAIL_BYTES = 64 * 1024
RUN_MARKER = "TOURNAMENT_AGENT_RUN"
MEMORY_POLL_S = 0.25
ENV_ALLOWLIST = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "LD_LIBRARY_PATH", "SYSTEMROOT", "TEMP", "TMP", "TMPDIR")

TIMEOUT = "timeout"
CRASH = "crash"
EXCEPTION = "exception"
MALFORMED = "malformed_response"
ILLEGAL = "illegal_action"
LOAD_ERROR = "load_error"
MEMORY = "memory_limit"
FORBIDDEN = "forbidden_import"

_EOF = object()


class AgentFailure(Exception):
    """An agent broke the rules or stopped working. It costs that agent the game."""

    def __init__(self, kind: str, detail: str = ""):
        super().__init__(f"{kind}: {detail}" if detail else kind)
        self.kind = kind
        self.detail = detail


class _Malformed:
    def __init__(self, detail: str):
        self.detail = detail


def scan_imports(path: Path, forbidden) -> None:
    """Reject syntax errors and forbidden imports before running anything."""
    try:
        tree = ast.parse(Path(path).read_bytes(), filename=str(path))
    except (SyntaxError, ValueError) as error:
        raise AgentFailure(LOAD_ERROR, f"{Path(path).name} cannot be parsed: {error}") from error
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            names = [base] + [f"{base}.{alias.name}" for alias in node.names]
        else:
            continue
        for name in names:
            for banned in forbidden:
                if name == banned or name.startswith(banned + "."):
                    raise AgentFailure(FORBIDDEN, f"{Path(path).name} imports {name} (line {node.lineno})")


class AgentProcess:
    """One agent, one process. See agent_host.py for the other end of the pipe."""

    def __init__(self, path, mode: str, label: str = "", seed: int = 1, memory_limit_mb: int = 2048, forbidden_imports=(), cpu=None):
        self.path = Path(path).resolve()
        self.mode = mode
        self.label = label or self.path.stem
        self.seed = seed
        self.memory_limit_mb = memory_limit_mb
        self.forbidden_imports = tuple(forbidden_imports)
        self.cpu = cpu
        self.proc = None
        self._inbox: queue.Queue = queue.Queue(maxsize=4096)
        self._outbox: queue.Queue = queue.Queue()
        self._stderr = collections.deque()
        self._stderr_size = 0
        self._seq = 0
        self._stopped = threading.Event()
        self._memory_exceeded = False
        self._paused = False
        self._work_dir = None
        self._run_id = uuid.uuid4().hex

    # ---------------------------------------------------------------- lifecycle

    def start(self, timeout_s: float) -> None:
        scan_imports(self.path, self.forbidden_imports)
        self._work_dir = tempfile.mkdtemp(prefix="agent_")
        env = {key: os.environ[key] for key in ENV_ALLOWLIST if key in os.environ}
        env.update(
            HOME=self._work_dir,
            PYTHONHASHSEED="0",
            PYTHONDONTWRITEBYTECODE="1",
            **{RUN_MARKER: self._run_id},
            OMP_NUM_THREADS="1",
            OPENBLAS_NUM_THREADS="1",
            MKL_NUM_THREADS="1",
        )
        spawn = {"start_new_session": True} if os.name == "posix" else {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        self.proc = subprocess.Popen(
            [sys.executable, "-u", str(HOST_SCRIPT), str(self.path), self.mode, str(self.seed), str(self.memory_limit_mb)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._work_dir,
            env=env,
            **spawn,
        )
        if self.cpu is not None:
            try:
                psutil.Process(self.proc.pid).cpu_affinity([self.cpu])
            except (AttributeError, psutil.Error, ValueError):
                pass
        for target in (self._read_protocol, self._read_stderr, self._write_protocol, self._watch_memory):
            threading.Thread(target=target, daemon=True).start()
        self._wait_ready(timeout_s)
        if self.mode != "stream":
            self.pause()

    def _wait_ready(self, timeout_s: float) -> None:
        try:
            _, message = self._inbox.get(timeout=timeout_s)
        except queue.Empty:
            self.stop()
            raise AgentFailure(LOAD_ERROR, f"not ready after {timeout_s:.0f} s (top-level code too slow?)") from None
        if message is _EOF:
            kind = MEMORY if self._memory_exceeded else LOAD_ERROR
            raise AgentFailure(kind, "process ended while loading\n" + self.stderr_tail())
        if not isinstance(message, dict) or message.get("type") != "ready":
            error = message.get("error", "") if isinstance(message, dict) else "unexpected output"
            self.stop()
            raise AgentFailure(LOAD_ERROR, error)

    def stop(self) -> None:
        if self._stopped.is_set():
            return
        self._stopped.set()
        if self.proc is not None:
            self._kill_tree()
            self._kill_escaped()
            # Closing can block while a reader thread is mid-read, and stop() must never block.
            threading.Thread(target=self._close_pipes, daemon=True).start()
        self._outbox.put(None)
        if self._work_dir:
            shutil.rmtree(self._work_dir, ignore_errors=True)
            self._work_dir = None

    def _kill_escaped(self) -> None:
        """A process that detached itself left the group, but it still carries the marker."""
        for process in psutil.process_iter(["environ"]):
            try:
                if (process.info["environ"] or {}).get(RUN_MARKER) == self._run_id:
                    process.kill()
            except psutil.Error:
                pass

    def _close_pipes(self) -> None:
        for pipe in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            try:
                pipe.close()
            except (OSError, ValueError):
                pass

    def _kill_tree(self) -> None:
        if self.proc is None:
            return
        try:
            children = psutil.Process(self.proc.pid).children(recursive=True)
        except psutil.Error:
            children = []
        if os.name == "posix":
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        else:
            try:
                self.proc.kill()
            except OSError:
                pass
        for child in children:
            try:
                child.kill()
            except psutil.Error:
                pass
        try:
            self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass

    def pause(self) -> None:
        """Between turns an agent gets no CPU, so it cannot think on the rival's time."""
        if self._paused or self.proc is None or self.proc.poll() is not None:
            return
        self._signal_group(signal.SIGSTOP if os.name == "posix" else None, suspend=True)
        self._paused = True

    def resume(self) -> None:
        if not self._paused or self.proc is None:
            return
        self._signal_group(signal.SIGCONT if os.name == "posix" else None, suspend=False)
        self._paused = False

    def _signal_group(self, signum, suspend: bool) -> None:
        try:
            if signum is not None:
                os.killpg(self.proc.pid, signum)
            else:
                process = psutil.Process(self.proc.pid)
                for item in [process] + process.children(recursive=True):
                    (item.suspend if suspend else item.resume)()
        except (ProcessLookupError, PermissionError, psutil.Error):
            pass

    # ------------------------------------------------------------------ threads

    def _read_protocol(self) -> None:
        stream = self.proc.stdout
        try:
            while True:
                line = stream.readline(MAX_LINE_BYTES + 1)
                now = time.monotonic()
                if not line:
                    break
                if len(line) > MAX_LINE_BYTES and not line.endswith(b"\n"):
                    while line and not line.endswith(b"\n"):
                        line = stream.readline(MAX_LINE_BYTES + 1)
                    self._inbox.put((now, _Malformed("message too long")))
                    continue
                try:
                    self._inbox.put((now, json.loads(line)))
                except ValueError:
                    self._inbox.put((now, _Malformed(repr(line[:200]))))
        except (OSError, ValueError):
            pass
        self._inbox.put((time.monotonic(), _EOF))

    def _read_stderr(self) -> None:
        try:
            for chunk in iter(lambda: self.proc.stderr.read1(8192), b""):
                self._stderr.append(chunk)
                self._stderr_size += len(chunk)
                while self._stderr_size > STDERR_TAIL_BYTES and len(self._stderr) > 1:
                    self._stderr_size -= len(self._stderr.popleft())
        except (OSError, ValueError):
            pass

    def _write_protocol(self) -> None:
        while True:
            data = self._outbox.get()
            if data is None:
                return
            try:
                self.proc.stdin.write(data)
                self.proc.stdin.flush()
            except (OSError, ValueError):
                return

    def _watch_memory(self) -> None:
        limit = self.memory_limit_mb * 1024 * 1024
        while not self._stopped.wait(MEMORY_POLL_S):
            try:
                process = psutil.Process(self.proc.pid)
                used = process.memory_info().rss
                for child in process.children(recursive=True):
                    used += child.memory_info().rss
            except psutil.Error:
                continue
            if used > limit:
                self._memory_exceeded = True
                self._kill_tree()
                return

    def stderr_tail(self, max_chars: int = 2000) -> str:
        text = b"".join(list(self._stderr)).decode("utf-8", "replace")
        return text[-max_chars:]

    # ----------------------------------------------------------------- protocol

    def _send(self, message: dict) -> None:
        self._outbox.put((json.dumps(message) + "\n").encode("utf-8"))

    def _death(self) -> AgentFailure:
        if self._memory_exceeded:
            return AgentFailure(MEMORY, f"used more than {self.memory_limit_mb} MB")
        return AgentFailure(CRASH, "process ended unexpectedly\n" + self.stderr_tail())

    def request(self, observation: dict, timeout_s: float):
        """Send one observation and wait for the answer. Returns (response, seconds)."""
        self._seq += 1
        message_id = self._seq
        payload = (json.dumps({"type": "observation", "id": message_id, "observation": observation}) + "\n").encode("utf-8")
        started = time.monotonic()
        deadline = started + timeout_s
        self.resume()
        self._outbox.put(payload)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._kill_tree()
                raise AgentFailure(TIMEOUT, f"no answer within {timeout_s:.2f} s")
            try:
                received, message = self._inbox.get(timeout=remaining)
            except queue.Empty:
                continue
            if message is _EOF:
                raise self._death()
            if isinstance(message, _Malformed):
                self._kill_tree()
                raise AgentFailure(MALFORMED, message.detail)
            if not isinstance(message, dict):
                self._kill_tree()
                raise AgentFailure(MALFORMED, repr(message)[:200])
            if message.get("type") == "error":
                self._kill_tree()
                raise AgentFailure(EXCEPTION, message.get("error", ""))
            if message.get("type") == "response" and message.get("id") == message_id:
                self.pause()
                return message.get("response"), received - started

    def send_problem(self, problem: dict) -> None:
        """Stream mode: hand over the one and only problem."""
        self._send({"type": "observation", "id": 0, "observation": problem})

    def drain(self, limit: int = 256):
        """Stream mode: what the agent has said so far, as (time, message) pairs."""
        items = []
        for _ in range(limit):
            try:
                received, message = self._inbox.get_nowait()
            except queue.Empty:
                break
            if message is _EOF:
                items.append((received, {"type": "exit"}))
            elif isinstance(message, _Malformed) or not isinstance(message, dict):
                items.append((received, {"type": "malformed"}))
            else:
                items.append((received, message))
        return items

    def death_reason(self) -> str:
        return MEMORY if self._memory_exceeded else CRASH


class SubprocessPlayer:
    """A turn-based player backed by a student's process."""

    def __init__(self, process: AgentProcess, startup_timeout_s: float):
        self.process = process
        self.startup_timeout_s = startup_timeout_s

    def start(self) -> None:
        self.process.start(self.startup_timeout_s)

    def decide(self, observation: dict, budget_s: float):
        return self.process.request(observation, budget_s)

    def stop(self) -> None:
        self.process.stop()

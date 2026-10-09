#!/usr/bin/env python3
"""Safe read-merge-write for the ONE per-session state file (RMP-21).

Live bug (2026-09-29, local stack): the gate said "Reach Machine, Apify, and
the browser not yet connected" for about 10 seconds, right after
`open_workspace`, although all three probes had passed and been recorded
earlier. The state file lost its probe keys and got them back only when the
model re-ran the probes.

Cause: about twenty hooks write this file (`connection_state.write_patch`),
and Claude Code runs the hooks of parallel tool calls at the same moment.
The old write was "read the file, merge, `write_text`" -- `write_text`
empties the file first. A second hook that read during that moment saw an
empty file, read it as `{}`, and wrote back only its own keys. Every other
key -- the probes included -- was gone. Reproduced with 8 processes writing
30 keys each: only 2 of 240 writes survived and the probe keys were lost.

Two fixes, both needed:
- a lock (`flock` on a sibling `.lock` file) so two writers never overlap;
- a temp file + `os.replace`, so a reader (the gate reads with no lock) sees
  the whole old file or the whole new file, never half of one.

RMP-76 (same race, other files): every hook file that is read, changed and
written back by more than one process goes through these helpers -- plan cache,
business-ready poll, job budget counter, the pending-checks queue, and the small
debug logs. `locked` + `write_atomic` are the building blocks.

FAIL-SAFE: never raises, never hangs. If the lock cannot be taken within
`_LOCK_WAIT_S` (or `fcntl` does not exist, e.g. Windows) the update still
runs -- the atomic replace alone already stops the total wipe.
"""
from __future__ import annotations

import contextlib
import json
import os
import pathlib
import time
from typing import Any, Callable

try:
    import fcntl
except ImportError:  # Windows: no flock; the atomic replace still applies
    fcntl = None  # type: ignore[assignment]

_LOCK_WAIT_S = 2.0
_LOCK_POLL_S = 0.005


def _take_lock(lock_path: pathlib.Path):
    """An open, locked file object, or None when no lock could be taken."""
    if fcntl is None:
        return None
    try:
        handle = open(lock_path, "a+")
    except Exception:
        return None
    deadline = time.monotonic() + _LOCK_WAIT_S
    while True:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return handle
        except OSError:
            if time.monotonic() >= deadline:
                handle.close()
                return None
            time.sleep(_LOCK_POLL_S)


@contextlib.contextmanager
def locked(path: pathlib.Path):
    """Hold the lock for `path` (a sibling `.lock` file) for the `with` body,
    so a caller can read, change and write as one step. Never raises on the
    lock itself; see the module docstring for the fail-safe."""
    handle = _take_lock(path.with_name(path.name + ".lock"))
    try:
        yield
    finally:
        if handle is not None:
            try:
                handle.close()  # closing releases the flock
            except Exception:
                pass


def write_atomic(path: pathlib.Path, text: str) -> None:
    """Whole-file replace: a reader sees the old file or the new one, never half.
    Raises on failure -- callers keep their own `try`."""
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def update_json(path: pathlib.Path, read: Callable[[], dict[str, Any]], patch: dict[str, Any]) -> None:
    """Merge `patch` onto the current content (from `read`) and replace the
    file atomically, holding the lock across read and write. Never raises."""
    try:
        with locked(path):
            write_atomic(path, json.dumps({**read(), **patch}))
    except Exception:
        pass


def modify_json(path: pathlib.Path, read: Callable[[], dict[str, Any]], mutate: Callable[[dict[str, Any]], Any]) -> Any:
    """Read (via `read`), let `mutate` change that dict in place, write it back
    atomically, all under the lock. Returns whatever `mutate` returned
    (None if anything failed). Never raises."""
    try:
        with locked(path):
            current = read()
            result = mutate(current)
            write_atomic(path, json.dumps(current))
            return result
    except Exception:
        return None


def append_trimmed_line(path: pathlib.Path, line: str, max_lines: int) -> None:
    """Append one line to a small log file, keep the last `max_lines`, under
    the lock and atomically. Creates the folder. Never raises."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with locked(path):
            lines: list[str] = []
            if path.exists():
                lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
            lines.append(line)
            write_atomic(path, "\n".join(lines[-max_lines:]) + "\n")
    except Exception:
        pass

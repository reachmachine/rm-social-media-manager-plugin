#!/usr/bin/env python3
"""Path safety checks for a customer-named file/folder (RMP-194 part 4).

Pure, filesystem-reading functions -- no network, no state file, easy to
unit-test with a real `tmp_path`. Split out of `customer_file_upload.py` to
keep that file (the HTTP-upload side) small and this one (the security
checks) independently testable.

Every rule here comes straight from the design doc's "Path safety" list:
  1. The path must appear in the customer's own last typed message.
  2. expanduser, then resolve; it must exist.
  3. Refuse whole-home/drive roots, system folders, dot-files/dot-folders,
     and secret-looking names.
  4. Folders are read ONE level deep only -- a subfolder is skipped, never
     recursed into. Hidden files are skipped. A symlink that resolves
     outside the folder is skipped. At most MAX_FILES are taken.
  5. Allowed extensions; a legacy `.doc`/`.xls` gets its own line.
  6. 20 MB per file, 50 MB per batch -- checked here, before any upload.
  7. (RMP-288) A bare file NAME the customer typed ("menu.pdf") is looked up inside the
     named folder `FILES_FOLDER_NAME` (made if missing) -- never anywhere else. A name
     with a slash, "..", "~", a drive colon or an absolute path is not a bare name: it
     is never joined to the folder, and a file there that is really a link pointing
     out of the folder is refused.

Refuses fail CLOSED (return an error key, never a guess); a folder scan's
per-entry problems (wrong extension, too big, hidden, a symlink pointing
out) are SKIPPED, never a hard refusal for the whole batch -- only an empty
result after skipping everything refuses.
"""
from __future__ import annotations

import os
from pathlib import Path

from customer_upload_kinds import is_legacy_extension, kind_for_name

# Must equal backend `customer_upload_say.FILES_FOLDER_NAME` (a backend test pins both).
FILES_FOLDER_NAME = "ReachMachine Files"
MAX_FILES = 20
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_BATCH_BYTES = 50 * 1024 * 1024

_SYSTEM_DIR_NAMES = frozenset({
    "windows", "program files", "program files (x86)", "programdata",
    "system32", "syswow64", "etc", "proc", "sys", "bin", "sbin", "usr",
    "boot", "library", "system", "system volume information",
})

_SECRET_NAME_HINTS = (
    "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", ".pem", ".key", ".kdbx", ".pfx", ".p12",
)


def normalize_for_match(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1]
    s = s.replace("\\", "/")
    while "//" in s:
        s = s.replace("//", "/")
    return s.rstrip("/").casefold()


def path_in_last_prompt(raw_path: str, last_prompt: str) -> bool:
    """True when `raw_path` (normalized for slash/quote style) is a
    substring of the customer's own last typed message. Stops the model
    naming a path it made up. Break: always return True -> RED (Rule 3
    test)."""
    if not raw_path or not last_prompt:
        return False
    return normalize_for_match(raw_path) in normalize_for_match(last_prompt)


def _is_drive_or_home_root(p: Path) -> bool:
    try:
        home = Path.home()
    except Exception:
        home = None
    return p == Path(p.anchor) or (home is not None and p == home)


def _touches_system_dir(p: Path) -> bool:
    return any(part.casefold() in _SYSTEM_DIR_NAMES for part in p.parts)


def _is_dotfile_or_dotfolder(p: Path) -> bool:
    return any(part.startswith(".") and part not in (".", "..") for part in p.parts)


def _looks_secret(p: Path) -> bool:
    name = p.name.casefold()
    return any(hint in name for hint in _SECRET_NAME_HINTS)


def _resolve_within(child: Path, parent: Path) -> bool:
    """True unless `child` is a symlink resolving OUTSIDE `parent` -- a
    symlink pointing INSIDE the same folder, or a plain file, both pass."""
    try:
        real = child.resolve()
        real_parent = parent.resolve()
    except Exception:
        return False
    return real == real_parent or real_parent in real.parents


def _one_level_children(folder: Path) -> list[Path]:
    """Immediate children only -- a subfolder is skipped outright, never
    recursed into (design doc rule 4). Hidden entries and symlinks that
    resolve outside `folder` are also skipped here."""
    out: list[Path] = []
    try:
        entries = sorted(os.scandir(folder), key=lambda e: e.name)
    except Exception:
        return out
    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_dir(follow_symlinks=False):
            continue  # one level deep only -- never recurse
        if not entry.is_file(follow_symlinks=True):
            continue
        child = Path(entry.path)
        if not _resolve_within(child, folder):
            continue
        out.append(child)
    return out


def _extension_ok(p: Path) -> str | None:
    """Returns the file's kind, or None when unsupported (including legacy
    `.doc`/`.xls`, which the caller reports with its own refusal for a
    SINGLE named file, but is just skipped inside a folder scan)."""
    if is_legacy_extension(p.name):
        return None
    return kind_for_name(p.name)


def ensure_files_folder(base: Path | None = None) -> Path | None:
    """Make the named folder in `base` (the folder Claude runs in; default: here) if it is missing.
    Returns it, or None when it cannot be made. Never raises."""
    folder = (base if base is not None else Path.cwd()) / FILES_FOLDER_NAME
    try:
        folder.mkdir(exist_ok=True)
    except Exception:
        return None
    return folder


def _is_bare_name(raw: str) -> bool:
    name = raw.strip().strip("'\"")
    return bool(name) and name not in (".", "..") and not any(c in name for c in "/\\:~\0")


def _folder_candidate(raw_path: str, base: Path | None) -> tuple[Path, Path] | None:
    """(the named folder, the bare name inside it) when `raw_path` is a bare name that exists there."""
    if not _is_bare_name(raw_path):
        return None
    folder = (base if base is not None else Path.cwd()) / FILES_FOLDER_NAME
    candidate = folder / raw_path.strip().strip("'\"")
    try:
        return (folder, candidate) if candidate.exists() else None
    except Exception:
        return None


def resolve_in_files_folder(raw_path: str, base: Path | None = None) -> Path | None:
    """A bare file name typed by the customer -> that file inside the named folder, or None
    (not a bare name, not there, or a link that points out of the folder)."""
    found = _folder_candidate(raw_path, base)
    return found[1] if found is not None and _resolve_within(found[1], found[0]) else None


def screen_path(raw_path: str, last_prompt: str, base: Path | None = None) -> tuple[list[Path], str | None]:
    """The whole guard, in order. Returns `(files, None)` on success (never
    empty) or `([], reason_key)` on refusal -- `reason_key` is one of
    `customer_upload_say.REFUSAL_LINES`'s keys."""
    if not path_in_last_prompt(raw_path, last_prompt):
        return [], "not_typed"

    expanded = os.path.expanduser(raw_path.strip().strip("'\""))
    in_folder = _folder_candidate(raw_path, base)
    if in_folder is not None and not _resolve_within(in_folder[1], in_folder[0]):
        return [], "symlink"  # a link inside the named folder that points out of it
    candidate = resolve_in_files_folder(raw_path, base) or Path(expanded)
    try:
        resolved = candidate.resolve()
    except Exception:
        return [], "not_found"
    if not resolved.exists():
        return [], "not_found"

    if _is_drive_or_home_root(resolved):
        return [], "root"
    if _touches_system_dir(resolved):
        return [], "system"
    if _is_dotfile_or_dotfolder(resolved):
        return [], "dotfile"
    if _looks_secret(resolved):
        return [], "secret"

    if resolved.is_file():
        if is_legacy_extension(resolved.name):
            return [], "ext_legacy"
        kind = kind_for_name(resolved.name)
        if kind is None:
            return [], "ext_unsupported"
        try:
            size = resolved.stat().st_size
        except Exception:
            return [], "not_found"
        if size > MAX_FILE_BYTES:
            return [], "too_big"
        return [resolved], None

    if resolved.is_dir():
        children = _one_level_children(resolved)
        usable: list[Path] = []
        total_bytes = 0
        for child in children:
            if len(usable) >= MAX_FILES:
                break  # "at most MAX_FILES are taken" -- truncate, not refuse
            if _extension_ok(child) is None:
                continue
            try:
                size = child.stat().st_size
            except Exception:
                continue
            if size > MAX_FILE_BYTES:
                continue
            usable.append(child)
            total_bytes += size
        if not usable:
            return [], "ext_unsupported"
        if total_bytes > MAX_BATCH_BYTES:
            return [], "batch_too_big"
        return usable, None

    return [], "not_found"

#!/usr/bin/env python3
"""File-kind classification for customer document uploads (RMP-194 part 4).

MIRRORS the server's own limits (`backend/app/services/customer_upload_
kinds.py`), the same "mirror, don't import" pattern RMP-172's
`website_upload.py` uses for `RawShopEvidence` -- this plugin has no access
to the backend codebase at all, and must use only the Python standard
library (RMP-76: nothing can be pip-installed on the customer's machine).
Keep the two files' constants in sync by hand.
"""
from __future__ import annotations

EXTENSION_KINDS: dict[str, str] = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".csv": "csv",
    ".txt": "text",
    ".md": "text",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".webp": "image",
}

LEGACY_EXTENSIONS: frozenset[str] = frozenset({".doc", ".xls"})

# Only these are worth gzip-ping on the upload leg (design doc, Part 3):
# text compresses ~3x; PDF/DOCX/XLSX/images are already-compressed
# containers, so gzipping them wastes CPU for ~1.0x.
GZIP_WORTH_IT_KINDS: frozenset[str] = frozenset({"text", "csv"})


def _ext(name: str) -> str:
    dot = name.rfind(".")
    return name[dot:].lower() if dot != -1 else ""


def kind_for_name(name: str) -> str | None:
    return EXTENSION_KINDS.get(_ext(name))


def is_legacy_extension(name: str) -> bool:
    return _ext(name) in LEGACY_EXTENSIONS


def gzip_worth_it(kind: str) -> bool:
    return kind in GZIP_WORTH_IT_KINDS

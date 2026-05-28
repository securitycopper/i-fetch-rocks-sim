"""
Minimal drive binary loader for MemoryBaySignal.

Loads a gzipped 16-bit memory image from a drive payload UUID.
No dependency on the CPU programmer package.

Set ``drives_dir`` before loading saves if you want memory bays to be
initialised from their drive files::

    from ifetchrocks_sim import _drive_loader
    _drive_loader.drives_dir = "game_app_data/Drives"

If ``drives_dir`` is None (the default), bays will initialise to all-zero memory.
"""
from __future__ import annotations

import base64
import gzip
import os
from typing import List, Optional

drives_dir: Optional[str] = None

_ENCODING = 'cp1252'
_RESERVED_BYTES = 4
_WORDS = 65536


def load_drive_words(payload: str) -> List[int]:
    """Return a 65536-element list of 16-bit ints from a drive payload.

    *payload* is either:
    - A UUID string (e.g. ``"c91c3493-e29e-40f6-bc84-1be4ec772b8b"``) pointing
      to a ``<drives_dir>/<uuid>.bin`` gzipped file.
    - A legacy base64 string (older saves).

    Returns all-zero memory if ``drives_dir`` is not set or the file is missing.
    """
    memory = [0] * _WORDS

    # Detect UUID vs legacy base64 by length (UUID = 36 chars with hyphens)
    is_uuid = len(payload) == 36 and payload.count('-') == 4

    if is_uuid:
        if drives_dir is None:
            return memory
        path = os.path.join(drives_dir, f"{payload}.bin")
        if not os.path.exists(path):
            return memory
        try:
            with gzip.open(path, 'rb') as f:
                raw = f.read()
        except Exception:
            return memory
        data = list(raw[_RESERVED_BYTES:])
    else:
        try:
            binary_encoding = payload.encode(_ENCODING)
            data = list(base64.b64decode(binary_encoding))
        except Exception:
            return memory

    for i in range(min(_WORDS, len(data) // 2)):
        lower = data[i * 2]
        upper = data[i * 2 + 1]
        memory[i] = (upper << 8) | lower

    return memory

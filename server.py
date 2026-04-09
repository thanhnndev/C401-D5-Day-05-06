"""ASGI entrypoint: đặt `src/` và gốc repo lên `sys.path` trước khi import `api`.

Chạy (không cần `export PYTHONPATH=src`)::

    uvicorn server:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / 'src'
for _p in (_SRC, _ROOT):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from api.app import app

__all__ = ['app']

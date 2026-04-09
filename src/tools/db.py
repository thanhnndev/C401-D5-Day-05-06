"""
Agent SPEC: ID `vinuni_*` + tool LangChain — ủy quyền sang `schemaDB_Excuted_.py` (PostgreSQL thật).
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from telemetry.logger import logger
from tools.schemaDB_Excuted_ import (
    DATABASE_CONFIG,
    execute_select,
    introspect_for_db_type,
)

DB_ID_ACADEMIC = 'vinuni_academic'
DB_ID_CTSV = 'vinuni_ctsv'

_DB_ALIASES: dict[str, str] = {
    'sis_db': DB_ID_ACADEMIC,
    'lms_db': DB_ID_CTSV,
}

# Map ID SPEC (graph / prompt) → key kỹ thuật trong schemaDB_Excuted_.DATABASE_CONFIG
_VINUNI_TO_DB_TYPE: dict[str, str] = {
    DB_ID_ACADEMIC: 'academic',
    DB_ID_CTSV: 'ctsv_booking',
}


def _canonical_db_id(db_id: str) -> str:
    raw = (db_id or '').strip()
    return _DB_ALIASES.get(raw, raw)


def _db_type_for_vinuni(cid: str) -> str | None:
    return _VINUNI_TO_DB_TYPE.get(cid)


DB_REGISTRY = [
    {
        'id': DB_ID_ACADEMIC,
        'description': DATABASE_CONFIG['academic']['description'],
        'dialect': 'postgresql',
        'keywords': [
            'sinh viên',
            'K67',
            'GPA',
            'học phí',
            'tuition',
            'mssv',
            'invoice',
        ],
    },
    {
        'id': DB_ID_CTSV,
        'description': DATABASE_CONFIG['ctsv_booking']['description'],
        'dialect': 'postgresql',
        'keywords': [
            'đặt phòng',
            'phòng học',
            'booking',
            'CTSV',
            'study_rooms',
        ],
    },
]


@tool
def get_db_list() -> str:
    """Bước 1: chọn DB — `vinuni_academic` (DATABASE_URL) vs `vinuni_ctsv` (CTSV_DATABASE_URL)."""
    header = '## REGISTRY — 2 DATABASE (PostgreSQL)\n\n'
    entries = []
    for db in DB_REGISTRY:
        entry = (
            f'### ID: `{db["id"]}`\n'
            f'- **Mô tả**: {db["description"]}\n'
            f'- **Dialect**: {db["dialect"]}\n'
            f'- **Gợi ý từ khóa**: {", ".join(db["keywords"])}\n'
        )
        entries.append(entry)
    legacy = (
        '\n---\n'
        '**Alias:** `sis_db` → `vinuni_academic`, `lms_db` → `vinuni_ctsv`.\n'
        '**Key kỹ thuật** (module `schemaDB_Excuted_.py`): `academic`, `ctsv_booking`.\n'
    )
    return header + '\n---\n'.join(entries) + legacy


def get_db_schema(db_id: str) -> str:
    cid = _canonical_db_id(db_id)
    dt = _db_type_for_vinuni(cid)
    if not dt:
        return f"Error: Database ID '{db_id}' không hợp lệ."
    inner = introspect_for_db_type(dt)
    if inner.startswith('Error:'):
        return inner
    return f'## Database `{cid}` (key: `{dt}`)\n\n{inner}'


def execute_sql(db_id: str, sql: str) -> dict[str, Any]:
    """JSON cho agent: `execute_sql_tool` — PostgreSQL qua `schemaDB_Excuted_.execute_select`."""
    cid = _canonical_db_id(db_id)
    dt = _db_type_for_vinuni(cid)
    if not dt:
        return {
            'ok': False,
            'error': (
                f"Database ID không hợp lệ: '{db_id}'. "
                f'Dùng {DB_ID_ACADEMIC} hoặc {DB_ID_CTSV}.'
            ),
            'rows': [],
            'row_count': 0,
            'db_id': cid,
        }

    url = DATABASE_CONFIG[dt]['url_getter']()
    logger.log_event(
        'SQL_EXEC',
        {
            'db_id': cid,
            'db_type': dt,
            'sql_preview': (sql or '')[:500],
            'has_url': url is not None,
        },
    )

    payload = execute_select(dt, sql)
    out: dict[str, Any] = {**payload, 'db_id': cid}
    out.pop('db_type', None)
    return out


@tool
def get_db_schema_tool(db_id: str) -> str:
    """Lấy schema PostgreSQL (public) cho `db_id` SPEC (`vinuni_*`)."""
    return get_db_schema(db_id)


@tool
def execute_sql_tool(db_id: str, sql: str) -> str:
    """Chạy SELECT read-only; kết quả JSON (rows dict) từ PostgreSQL thật."""
    payload = execute_sql(db_id, sql)
    return json.dumps(payload, ensure_ascii=False)


DB_AGENT_TOOLS = [get_db_list, get_db_schema_tool, execute_sql_tool]

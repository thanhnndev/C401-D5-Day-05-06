"""
PostgreSQL read-only: introspection + SELECT (hai DB — academic / ctsv_booking).

Đây là lớp lõi; agent dùng `tools.db` (ID SPEC `vinuni_*`) gọi vào đây.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import psycopg
from langchain_core.tools import tool
from psycopg.rows import dict_row

from config import get_ctsv_database_url, get_database_url

DATABASE_CONFIG: dict[str, dict[str, Any]] = {
    'academic': {
        'url_getter': get_database_url,
        'description': (
            'Dữ liệu học vụ, GPA, học phí, sinh viên (VinUni academic — `DATABASE_URL`).'
        ),
        'env_var': 'DATABASE_URL',
    },
    'ctsv_booking': {
        'url_getter': get_ctsv_database_url,
        'description': (
            'CTSV: đặt phòng học (`study_rooms`, `room_bookings`) — `CTSV_DATABASE_URL`.'
        ),
        'env_var': 'CTSV_DATABASE_URL',
    },
}

_MAX_ROWS = 1000
_STATEMENT_TIMEOUT_MS = 30_000

_DANGEROUS_SQL = re.compile(
    r'\b(DROP|DELETE|INSERT|UPDATE|TRUNCATE|ALTER|CREATE|GRANT|REVOKE)\b',
    re.IGNORECASE | re.DOTALL,
)


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (bytes, memoryview)):
        return value.decode('utf-8', errors='replace')
    return value


def _validate_select_readonly(query: str) -> str | None:
    s = (query or '').strip()
    if not s:
        return 'SQL rỗng.'
    low = s.lower()
    if not (low.startswith('select') or low.startswith('with')):
        return 'Chỉ cho phép SELECT hoặc WITH … SELECT (read-only).'
    if _DANGEROUS_SQL.search(s):
        return 'Câu lệnh chứa từ khóa không được phép (read-only).'
    if ';' in s.rstrip(';').rstrip():
        return 'Không hỗ trợ nhiều câu lệnh (;). Một câu duy nhất.'
    low2 = s.lower()
    forbidden_keywords = [
        'insert',
        'update',
        'delete',
        'drop',
        'truncate',
        'alter',
        'grant',
        'revoke',
        'create',
        'upsert',
    ]
    for word in forbidden_keywords:
        if re.search(rf'\b{word}\b', low2):
            return f"Lệnh '{word.upper()}' bị cấm (read-only)."
    return None


def introspect_schema_markdown(url: str) -> str:
    """Schema `public`: bảng + view, cột từ information_schema (an toàn tham số)."""
    lines: list[str] = ['### Schema (public)\n']
    try:
        with psycopg.connect(url, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type IN ('BASE TABLE', 'VIEW')
                    ORDER BY table_name
                    """
                )
                tables = cur.fetchall()
                if not tables:
                    lines.append('*(Không có bảng/view trong schema public.)*')
                    return '\n'.join(lines)

                for table_name, table_type in tables:
                    cur.execute(
                        """
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = %s
                        ORDER BY ordinal_position
                        """,
                        (table_name,),
                    )
                    cols = cur.fetchall()
                    kind = 'VIEW' if table_type == 'VIEW' else 'TABLE'
                    lines.append(f'#### {kind}: `{table_name}`')
                    for col_name, data_type, is_nullable in cols:
                        null = 'NULL' if is_nullable == 'YES' else 'NOT NULL'
                        lines.append(f'- `{col_name}` {data_type} {null}')
                    lines.append('')
    except Exception as e:
        return f'Error introspecting schema: {e!s}'
    return '\n'.join(lines).strip()


def introspect_for_db_type(db_type: str) -> str:
    if db_type not in DATABASE_CONFIG:
        return f"Error: Database '{db_type}' không tồn tại."
    url = DATABASE_CONFIG[db_type]['url_getter']()
    if not url:
        ev = DATABASE_CONFIG[db_type]['env_var']
        return f'Error: Cấu hình {db_type} ({ev}) chưa được thiết lập.'
    body = introspect_schema_markdown(url)
    return f'--- Schema cho DB: `{db_type}` ---\n\n{body}'


def execute_select(db_type: str, query: str) -> dict[str, Any]:
    """SELECT read-only → `{ok, db_type, row_count, rows, ...}`."""
    if db_type not in DATABASE_CONFIG:
        return {
            'ok': False,
            'error': f"Database '{db_type}' không tồn tại.",
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }

    err = _validate_select_readonly(query)
    if err:
        return {
            'ok': False,
            'error': err,
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }

    url = DATABASE_CONFIG[db_type]['url_getter']()
    if not url:
        ev = DATABASE_CONFIG[db_type]['env_var']
        return {
            'ok': False,
            'error': f'Chưa cấu hình biến môi trường {ev}.',
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }

    try:
        with psycopg.connect(url, connect_timeout=15) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # SET không hỗ trợ placeholder $1 trên mọi phiên bản — dùng ms (hằng số an toàn).
                cur.execute(f'SET statement_timeout = {_STATEMENT_TIMEOUT_MS}')
                cur.execute(query)
                rows = cur.fetchmany(_MAX_ROWS)
                safe = [_json_safe(dict(r)) for r in rows]
                return {
                    'ok': True,
                    'db_type': db_type,
                    'row_count': len(safe),
                    'rows': safe,
                    'read_only': True,
                    'hint': f'Tối đa {_MAX_ROWS} dòng; chỉ SELECT/WITH.',
                }
    except Exception as e:
        return {
            'ok': False,
            'error': str(e).strip()[:2000],
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }


def _rows_to_pipe_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '0 dòng.'
    cols = list(rows[0].keys())
    header = ' | '.join(cols)
    sep = '-' * len(header)
    out = [header, sep]
    for r in rows:
        out.append(' | '.join(str(r.get(c)) for c in cols))
    return '\n'.join(out)


@tool
def list_databases_tool() -> str:
    """
    Liệt kê các database có sẵn và mục đích.
    Tham số kỹ thuật: `academic` (DATABASE_URL) và `ctsv_booking` (CTSV_DATABASE_URL).
    """
    info = 'Các database khả dụng (key kỹ thuật → mô tả):\n'
    for db_type, cfg in DATABASE_CONFIG.items():
        info += f"- `{db_type}`: {cfg['description']} (env: {cfg['env_var']})\n"
    info += (
        '\nAgent SPEC dùng ID `vinuni_academic` / `vinuni_ctsv` qua `tools.db` '
        '(map sang academic / ctsv_booking).\n'
    )
    return info


@tool
def get_schema_tool(db_type: str) -> str:
    """
    Lấy schema (bảng/view và cột) của một database.
    Tham số db_type: `academic` hoặc `ctsv_booking`.
    """
    return introspect_for_db_type(db_type)


@tool
def execute_query_tool(db_type: str, query: str) -> str:
    """
    Thực thi SQL chỉ đọc (SELECT / WITH) trên DB đã chọn.
    Tham số db_type: `academic` hoặc `ctsv_booking`.
    """
    payload = execute_select(db_type, query)
    if not payload.get('ok'):
        return payload.get('error') or 'Lỗi không xác định.'

    rows: list[dict[str, Any]] = payload.get('rows') or []
    if not rows:
        return f'Kết quả từ {db_type}: 0 dòng.'

    table = _rows_to_pipe_table(rows)
    n = payload.get('row_count', len(rows))
    hint = payload.get('hint', '')
    return f'--- Kết quả từ {db_type} ({n} dòng) ---\n{hint}\n\n{table}'

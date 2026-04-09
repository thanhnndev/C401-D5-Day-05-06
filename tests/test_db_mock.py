"""Two-database mock (SPEC VinUni academic + CTSV) — registry and read-only guard."""

from __future__ import annotations

import json

from tools.db import (
    DB_ID_ACADEMIC,
    DB_ID_CTSV,
    execute_sql,
    execute_sql_tool,
    get_db_list,
)


def test_registry_lists_two_databases() -> None:
    text = get_db_list.invoke({})
    assert DB_ID_ACADEMIC in text
    assert DB_ID_CTSV in text
    assert 'Đào Tạo' in text or 'academic' in text.lower()
    assert 'CTSV' in text


def test_academic_mock_rows_and_row_count() -> None:
    out = execute_sql(DB_ID_ACADEMIC, 'SELECT * FROM students WHERE cohort = K67')
    assert out['ok'] is True
    assert out['db_id'] == DB_ID_ACADEMIC
    assert out['row_count'] >= 1
    assert isinstance(out['rows'], list)


def test_ctsv_campaign_mock() -> None:
    out = execute_sql(DB_ID_CTSV, 'SELECT * FROM email_campaigns')
    assert out['ok'] is True
    assert out['db_id'] == DB_ID_CTSV
    assert out['row_count'] >= 1
    assert 'campaign_id' in out['rows'][0]


def test_rejects_non_select() -> None:
    out = execute_sql(DB_ID_ACADEMIC, 'DELETE FROM students WHERE 1=1')
    assert out['ok'] is False
    assert out['row_count'] == 0


def test_alias_sis_db_maps_to_academic() -> None:
    out = execute_sql('sis_db', 'SELECT 1')
    assert out['ok'] is True
    assert out['db_id'] == DB_ID_ACADEMIC


def test_execute_sql_tool_returns_json_string() -> None:
    raw = execute_sql_tool.invoke(
        {'db_id': DB_ID_ACADEMIC, 'sql': 'SELECT * FROM students'}
    )
    data = json.loads(raw)
    assert 'row_count' in data
    assert 'rows' in data

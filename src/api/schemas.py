"""Pydantic models for chat and history API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """User message for one graph turn."""

    message: str = Field(
        ...,
        min_length=1,
        description='User text: mapped to `text` (stub graph) or initial HumanMessage (ReAct agent).',
    )
    thread_id: str | None = Field(
        None,
        description='Conversation thread; if omitted, server generates a UUID.',
    )


class ChatResponse(BaseModel):
    """Graph output for one turn."""

    thread_id: str
    state: dict[str, Any]


class HistoryCheckpointItem(BaseModel):
    """One snapshot from `get_state_history` (JSON-safe)."""

    values: dict[str, Any]
    metadata: dict[str, Any]
    created_at: str | None = None
    checkpoint_id: str | None = None
    parent_checkpoint_id: str | None = None


class HistoryResponse(BaseModel):
    """Ordered history for a thread (newest first per LangGraph iterator)."""

    thread_id: str
    checkpoints: list[HistoryCheckpointItem]


class DbInstanceStatus(BaseModel):
    """Reachability of one PostgreSQL instance (academic or CTSV)."""

    configured: bool = Field(
        description='True if the corresponding env URL (DATABASE_URL or CTSV_DATABASE_URL) is set.',
    )
    reachable: bool | None = Field(
        None,
        description='True if a simple SELECT 1 succeeds; False if configured but connection fails; null if not configured.',
    )
    error: str | None = Field(
        None,
        description='Short error message when configured and reachable is false.',
    )


class DatabasesHealth(BaseModel):
    """Two logical databases from project config."""

    academic: DbInstanceStatus = Field(
        description='Instance from DATABASE_URL (học vụ; LangGraph checkpoint may share this URI).',
    )
    ctsv: DbInstanceStatus = Field(
        description='Instance from CTSV_DATABASE_URL (đặt phòng CTSV).',
    )


class HealthResponse(BaseModel):
    """Liveness plus optional DB probes."""

    status: Literal['ok'] = 'ok'
    databases: DatabasesHealth

"""Voice module exceptions."""

from __future__ import annotations


class VoiceError(Exception):
    """Raised for voice input/output errors."""


class VadLoadError(VoiceError):
    """VAD model failed to load."""

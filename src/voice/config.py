"""Voice configuration for STT and VAD."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class VadBackend(StrEnum):
    auto = 'auto'
    silero = 'silero'
    rms = 'rms'


@dataclass
class VadConfig:
    """Configuration for voice activity detection."""

    backend: VadBackend = VadBackend.auto
    speech_threshold: float = 0.5
    min_silence_frames: int = 10
    silero_model_version: str = 'v5'
    silero_force_cpu: bool = False
    silero_device_cache: bool = True


@dataclass
class VoiceConfig:
    """Configuration for voice recording and transcription."""

    model_name: str = 'base.en'
    language: str = 'en'
    sample_rate: int = 16000
    silence_duration: float = 1.0
    energy_threshold: float = 0.01
    max_recording_sec: float = 60.0
    device_index: int | None = None
    audio_file: str | None = None
    input_mode: str = 'silence'
    # vad: VadConfig = field(default_factory=VadConfig)

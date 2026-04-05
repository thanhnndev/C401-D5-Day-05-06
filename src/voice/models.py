from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from pywhispercpp.model import Model

from .config import VoiceConfig


@runtime_checkable
class STTProvider(Protocol):
    def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int) -> str: ...
    def transcribe_file(self, file_path: str) -> str: ...
    def load(self) -> None: ...
    def unload(self) -> None: ...


class WhisperCppAdapter:
    def __init__(self, config: VoiceConfig) -> None:
        self._config = config
        self._model = Model(
            self._config.model_name,
            models_dir='models',
            redirect_whispercpp_logs_to='logs/whisper-cpp.logs',
        )

    def unload(self) -> None:
        self._model = None

    def transcribe_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
    ) -> str:

        if sample_rate != self._config.sample_rate:
            from scipy.signal import resample

            num_samples = int(len(audio_data) * self._config.sample_rate / sample_rate)
            audio_data = resample(audio_data, num_samples).astype(np.float32)

        result = self._model.transcribe(audio_data)

        text = result.text.strip() if hasattr(result, 'text') else str(result).strip()
        return text

    def transcribe_file(self, file_path: str) -> str:
        return ''.join(seg.text for seg in self._model.transcribe(file_path))

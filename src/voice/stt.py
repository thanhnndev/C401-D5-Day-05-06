from __future__ import annotations

import numpy as np

from .config import VoiceConfig
from .exceptions import VoiceError
from .models import STTProvider, WhisperCppAdapter
from .recorder import record_until_keypress


class VoiceSTT:
    def __init__(self, config: VoiceConfig | None = None) -> None:
        self._config = config or VoiceConfig()
        self._provider: STTProvider = WhisperCppAdapter(self._config)

    def transcribe(self) -> str:
        """Transcribe from mic or audio file. Returns text string."""
        try:
            if self._config.audio_file:
                pass
            elif self._config.input_mode == 'keypress':
                audio = record_until_keypress(self._config, 'output.wav')
                sr = self._config.sample_rate
            else:
                pass
                # audio = record_until_silence(self._config)
                # sr = self._config.sample_rate
        except VoiceError as exc:
            print(f'Voice input error: {exc}')
            return ''
        except KeyboardInterrupt:
            print('Recording cancelled.')
            return ''

        # if len(audio) == 0:
        #     print('No speech detected.')
        #     return ''

        try:
            text = self._provider.transcribe_file('output.wav')
            return text
        except Exception as exc:
            print(f'Transcription error: {exc}')
            return ''

    def transcribe_file(self, file_path: str) -> str:
        """Convenience: transcribe a specific audio file."""
        return self._provider.transcribe_file(file_path)

    def set_provider(self, provider: STTProvider) -> None:
        """Swap the STT provider at runtime."""
        self._provider = provider

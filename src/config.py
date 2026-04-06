from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class PipelineConfig:
    mock_mode: bool = True
    db_path: str = 'sqlite:///data.db'
    whisper_model: str = 'base'
    llm_provider: str = 'openai'
    llm_temperature: float = 0.0

    @classmethod
    def from_env(cls) -> PipelineConfig:
        return cls(
            mock_mode=os.getenv('MOCK_MODE', '1') == '1',
            db_path=os.getenv('DB_PATH', 'sqlite:///data.db'),
            whisper_model=os.getenv('WHISPER_MODEL', 'base'),
            llm_provider=os.getenv('LLM_PROVIDER', 'openai'),
            llm_temperature=float(os.getenv('LLM_TEMPERATURE', '0.0')),
        )

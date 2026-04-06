from __future__ import annotations

import io
import re

import pandas as pd
import streamlit as st
from gtts import gTTS
from pydub import AudioSegment


def decode_audio(audio_raw: dict | None) -> io.BytesIO | None:
    if not audio_raw:
        return None
    try:
        audio_bytes = audio_raw['bytes']
        segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        mp3_fp = io.BytesIO()
        segment.export(mp3_fp, format='mp3', bitrate='128k')
        mp3_fp.seek(0)
        return mp3_fp
    except Exception as exc:
        st.error(f'Audio decode failed: {exc}')
        return None


def speech2text(audio_data: io.BytesIO | None) -> str:
    """Audio -> Whisper model -> Text."""
    if not audio_data:
        return ''
    # TODO: replace body with real Whisper call
    return 'Danh sach 5 sinh vien co ket qua hoc tap thap nhat trong tuan dau tien'


def text2sql_dbquery(user_query: str) -> pd.DataFrame:
    """User query -> LLM generates SQL -> Execute -> DataFrame."""
    # TODO: replace body with real text2SQL + DB execution
    return pd.DataFrame({
        'Sinh vien': ['Hai Dang', 'Minh Ha', 'Duc An', 'Quang Hien'],
        'Diem TB': [2.1, 2.3, 2.8, 3.1],
    })


def data_visualization(queried_data: pd.DataFrame) -> dict:
    """DataFrame -> LLM generates Vega-Lite spec -> dict."""
    # TODO: replace with real LLM call
    return {
        'mark': {'type': 'bar', 'tooltip': True},
        'encoding': {
            'x': {'field': 'Sinh vien', 'type': 'nominal', 'axis': {'labelAngle': 0}},
            'y': {'field': 'Diem TB', 'type': 'quantitative'},
            'color': {'field': 'Sinh vien', 'type': 'nominal'},
        },
    }


def llm_analysis_data(user_query: str, queried_data: pd.DataFrame) -> str:
    """Query + DataFrame -> LLM generates analysis -> Text."""
    # TODO: replace with real LLM call
    return (
        f'Phan tich cho cau hoi: {user_query}\n'
        f'So lieu: {len(queried_data)} dong du lieu.\n'
        '(Noi dung analysis that se duoc sinh boi model)'
    )


def run_pipeline(user_query: str | None, audio_raw: dict | None) -> dict | None:
    # Stage 1: resolve user_query from audio or text
    if audio_raw and not user_query:
        audio_fp = decode_audio(audio_raw)
        if not audio_fp:
            return None  # error already shown by decode_audio
        user_query = speech2text(audio_fp)

    if not user_query:
        return None

    # Stage 2: SQL query
    try:
        df_result = text2sql_dbquery(user_query)
    except Exception as exc:
        st.error(f'Database query failed: {exc}')
        return None

    # Stage 3: LLM analysis + visualization
    try:
        llm_insight = llm_analysis_data(user_query, df_result)
    except Exception as exc:
        st.error(f'Analysis failed: {exc}')
        return None

    try:
        chart_spec = data_visualization(df_result)
    except Exception as exc:
        st.error(f'Visualization failed: {exc}')
        chart_spec = None

    return {
        'user_query': user_query,
        'data': df_result,
        'chart': chart_spec,
        'insight': llm_insight,
    }


def text2speech(text: str) -> io.BytesIO:
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    formatted = formatted.replace('\n', '<br>')
    tts = gTTS(text=formatted, lang='vi')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

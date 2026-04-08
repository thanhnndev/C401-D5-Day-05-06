from __future__ import annotations

import io
import json
import os
import re
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI
from pydub import AudioSegment

load_dotenv()

SCHEMA = (
    'students(student_id, first_name, last_name, email, enrollment_date, major) | '
    'courses(course_id, course_code, course_name, credits, department) | '
    'marks(mark_id, student_id, course_id, score, grade, semester, academic_year) | '
    'departments(department_id, department_name, faculty) | '
    'enrollments(enrollment_id, student_id, course_id, enrollment_status, enrollment_date)'
)

PROMPT_FILE = Path('src/prompts/text-to-sql.md')
SYSTEM_PROMPT = PROMPT_FILE.read_text().format(SCHEMA)

client = OpenAI(
    base_url=os.getenv('OLLAMA_BASE_URL'),
    api_key=os.getenv('OLLAMA_API_KEY'),
)


def run(sql: str) -> tuple[list[str] | None, list[tuple] | None]:
    """Execute SQL. Returns (cols, rows) or (None, None) on non-query."""
    conn = sqlite3.connect('data/db.db')
    cur = conn.execute(sql)
    if cur.description is None:
        print(f'{cur.rowcount} row(s) affected.')
        conn.close()
        return None, None
    rows = cur.fetchall()
    if not rows:
        print('No results.')
        conn.close()
        return None, None
    cols = [d[0] for d in cur.description]
    conn.close()
    return cols, rows


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
    try:
        # Reset pointer to start
        audio_data.seek(0)
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_data,
        )
        return transcription.text
    except Exception as exc:
        st.error(f'Whisper transcription failed: {exc}')
        return ''


def text2sql(message: str) -> dict:
    response = client.chat.completions.create(
        model=os.getenv('DEFAULT_MODEL'),
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': message},
        ],
        extra_body={'reasoning': {'enabled': False}},
    )
    content = response.choices[0].message.content

    # Robust JSON extraction
    try:
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx : end_idx + 1]
            return json.loads(json_str)
        return json.loads(content)
    except (json.JSONDecodeError, ValueError) as exc:
        st.error(f'Failed to parse LLM response: {exc}')
        # Fallback to empty spec if parsing fails
        return {'sql': 'SELECT 1 WHERE 1=0', 'viz': []}


def data_visualization(spec: dict) -> dict:
    """Pass through Vega-Lite spec from LLM to Streamlit with defaults."""
    encoding = spec.get('encoding', {}).copy()

    # Add default types if missing
    for axis in ['x', 'y', 'color']:
        if axis in encoding:
            if 'type' not in encoding[axis]:
                # Heuristic: if field name contains 'id', 'name', 'grade', 'status' -> nominal
                # if it contains 'score', 'credit', 'mark' -> quantitative
                field = str(encoding[axis].get('field', '')).lower()
                if any(k in field for k in ['id', 'name', 'grade', 'status', 'email', 'date', 'major']):
                    encoding[axis]['type'] = 'nominal'
                else:
                    encoding[axis]['type'] = 'quantitative'

    return {
        'mark': {'type': spec.get('type', 'bar')},
        'encoding': encoding,
    }


def llm_analysis_data(user_query: str, queried_data: pd.DataFrame) -> str:
    """Generate Vietnamese analysis of query results using LLM."""
    df_info = f'Columns: {list(queried_data.columns)}. Rows: {len(queried_data)}'
    prompt = (
        'Summarize the following data for a non-technical user in clear Vietnamese.\n'
        f'User query: {user_query}\n'
        f'Data summary: {df_info}\n'
        'Provide concise, actionable insights.'
    )
    try:
        response = client.chat.completions.create(
            model=os.getenv('DEFAULT_MODEL'),
            messages=[
                {'role': 'system', 'content': 'You are a helpful data analyst.'},
                {'role': 'user', 'content': prompt},
            ],
            extra_body={'reasoning': {'enabled': False}},
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f'Phân tích cho: {user_query}. Số dòng dữ liệu: {len(queried_data)}.'


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
        res = text2sql(user_query)
        print(res)
        sql_result = run(res['sql'])
        if sql_result[0] is None or sql_result[1] is None:
            return None
        df_result = pd.DataFrame(sql_result[1], columns=sql_result[0])
    except Exception as exc:
        st.error(f'Failed to extract sql and chart spec: {exc}')
        return None

    # Stage 3: LLM analysis + visualization
    try:
        llm_insight = llm_analysis_data(user_query, df_result)
    except Exception as exc:
        st.error(f'Analysis failed: {exc}')
        return None

    try:
        chart_specs = [data_visualization(v) for v in res['viz']] if res['viz'] else []
    except Exception as exc:
        st.error(f'Visualization failed: {exc}')
        chart_specs = []

    return {
        'user_query': user_query,
        'data': df_result,
        'chart': chart_specs,
        'insight': llm_insight,
    }


def clean_text_for_tts(text: str) -> str:
    """Removes Markdown and HTML tags for natural speech."""
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'[*#_`~]', '', text)
    return text.strip()


def text2speech(text: str) -> io.BytesIO | None:
    """Converts text to speech using gTTS with error handling."""
    try:
        clean_text = clean_text_for_tts(text)
        if not clean_text:
            return None
            
        tts = gTTS(text=clean_text, lang='vi')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        return None

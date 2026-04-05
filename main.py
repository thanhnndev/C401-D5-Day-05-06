import os
import re
import sqlite3

from dotenv import load_dotenv
from openai import OpenAI

from src.voice.config import VoiceConfig
from src.voice.stt import VoiceSTT

load_dotenv()

SYSTEM_PROMPT = (
    'You are a Text-to-SQL assistant. Generate precise SQLite queries '
    'based on the schema and user request. Return only SQL, no explanation. '
    'Ask for clarification if ambiguous. '
    'Schema: students(student_id, first_name, last_name, email, enrollment_date, major) | '
    'courses(course_id, course_code, course_name, credits, department) | '
    'marks(mark_id, student_id, course_id, score, grade, semester, academic_year) | '
    'departments(department_id, department_name, faculty) | '
    'enrollments(enrollment_id, student_id, course_id, enrollment_status, enrollment_date)'
)



def get_input(mode: str, client: OpenAI) -> str:
    if mode == 'text':
        return input('User > ')
    if mode == 'voice':
        config = VoiceConfig(input_mode='keypress')
        stt = VoiceSTT(config)
        trans = stt.transcribe()
        print(trans)
        return trans
    path = input('Audio file path > ').strip() or 'samples/voice_test.wav'
    with open(path, 'rb') as f:
        resp = client.audio.transcriptions.create(model='whisper-1', file=f)
    return resp.text


def to_sql(client: OpenAI, messages: list[dict]) -> str:
    stream = client.chat.completions.create(
        model='qwen/qwen3.6-plus:free',
        messages=messages,
        stream=True,
        extra_body={'reasoning': {'enabled': False}},
    )
    text = ''.join(chunk.choices[0].delta.content or '' for chunk in stream)
    print(text)
    return text


def run(sql: str) -> None:
    sql = re.sub(r'```.*?\n|```', '', sql).strip()
    conn = sqlite3.connect('data/db.db')
    cur = conn.execute(sql)
    if cur.description is None:
        print(f'{cur.rowcount} row(s) affected.')
        conn.close()
        return
    rows = cur.fetchall()
    if not rows:
        print('No results.')
        conn.close()
        return
    cols = [d[0] for d in cur.description]
    widths = [
        max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
        for i, c in enumerate(cols)
    ]
    print('  '.join(str(c).ljust(w) for c, w in zip(cols, widths, strict=True)))
    print('  '.join('-' * w for w in widths))
    for row in rows:
        print('  '.join(str(v).ljust(w) for v, w in zip(row, widths, strict=True)))
    conn.close()


def main() -> None:
    client = OpenAI(
        base_url='https://openrouter.ai/api/v1', api_key=os.getenv('OPENROUTER_API_KEY')
    )
    history = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    mode = input('Mode [text/voice/file] > ').strip().lower() or 'text'
    try:
        while True:
            prompt = get_input(mode, client)
            if not prompt.strip():
                break
            history.append({'role': 'user', 'content': prompt})
            sql = to_sql(client, history)
            history.append({'role': 'assistant', 'content': sql})
            run(sql)
    except KeyboardInterrupt:
        pass
    print('Goodbye')


if __name__ == '__main__':
    main()

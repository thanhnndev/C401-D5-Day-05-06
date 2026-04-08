from __future__ import annotations

import base64
import json
import operator
import os
import sqlite3
from typing import Annotated, Any, Literal, Optional, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.pipeline import clean_text_for_tts, text2speech

load_dotenv()

# Schema from src/pipeline.py
SCHEMA = (
    'students(student_id, first_name, last_name, email, enrollment_date, major) | '
    'courses(course_id, course_code, course_name, credits, department) | '
    'marks(mark_id, student_id, course_id, score, grade, semester, academic_year) | '
    'departments(department_id, department_name, faculty) | '
    'enrollments(enrollment_id, student_id, course_id, enrollment_status, enrollment_date)'
)


class AgentState(TypedDict):
    # History & Context
    messages: Annotated[list[BaseMessage], operator.add]
    query: str
    refined_query: Optional[str]

    # Execution State
    sql: Optional[str]
    sql_results: Optional[list[dict[str, Any]]]
    sql_error: Optional[str]
    retry_count: int

    # Final Outputs
    viz_specs: list[dict[str, Any]]
    primary_visual: Literal['table', 'chart', 'kpi']
    analysis: Optional[str]
    audio_base64: Optional[str]


# Initialize LLM
# Using ChatOpenAI with Ollama configuration if provided
llm = ChatOpenAI(
    model=os.getenv('DEFAULT_MODEL', 'gpt-4o'),
    base_url=os.getenv('OLLAMA_BASE_URL'),
    api_key=os.getenv('OLLAMA_API_KEY', 'ollama'),
    temperature=0,
)


def query_refinement(state: AgentState) -> dict[str, Any]:
    """Refine user query for better SQL generation."""
    messages = state.get('messages', [])
    query = state.get('query', '')

    prompt = f"""Bạn là một chuyên gia phân tích dữ liệu. Hãy tinh chỉnh yêu cầu sau đây của người dùng thành một câu truy vấn rõ ràng, chính xác dựa trên lược đồ cơ sở dữ liệu.

    Lược đồ: {SCHEMA}

    Yêu cầu người dùng: {query}

    Lịch sử hội thoại: {messages}

    Chỉ trả về câu truy vấn đã được tinh chỉnh bằng tiếng Việt, không thêm bất kỳ văn bản nào khác."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        'refined_query': response.content,
        'messages': [HumanMessage(content=query)],
    }


def text_to_sql(state: AgentState) -> dict[str, Any]:
    """Generate SQL from refined query."""
    query = state.get('refined_query') or state.get('query')
    sql_error = state.get('sql_error')
    retry_count = state.get('retry_count', 0)

    with open('src/prompts/text-to-sql.md') as f:
        system_prompt = f.read().format(SCHEMA)

    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]

    if sql_error:
        messages.append(
            HumanMessage(
                content=f'Truy vấn SQL trước đó đã thất bại với lỗi: {sql_error}. Vui lòng sửa lại.\nYêu cầu của tôi là: {query}'
            )
        )
    else:
        messages.append(HumanMessage(content=query))

    response = llm.invoke(messages)
    content = str(response.content)

    # Extract JSON
    try:
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx : end_idx + 1]
            res = json.loads(json_str)
        else:
            res = json.loads(content)

        return {
            'sql': res.get('sql'),
            'viz_specs': res.get('viz', []),
            'retry_count': retry_count,
        }
    except Exception as e:
        return {
            'sql_error': f'JSON parsing error: {str(e)}',
            'retry_count': retry_count + 1,
        }


def execute_sql(state: AgentState) -> dict[str, Any]:
    """Execute the generated SQL query."""
    sql = state.get('sql')
    retry_count = state.get('retry_count', 0)

    if not sql:
        return {'sql_error': 'No SQL generated', 'retry_count': retry_count + 1}

    try:
        conn = sqlite3.connect('data/db.db')
        df = pd.read_sql_query(sql, conn)
        conn.close()

        return {'sql_results': df.to_dict(orient='records'), 'sql_error': None}
    except Exception as e:
        return {'sql_error': str(e), 'retry_count': retry_count + 1}


def viz_generation(state: AgentState) -> dict[str, Any]:
    """Refine visualization specs and determine primary visual type."""
    data = state.get('sql_results', [])
    viz_specs = state.get('viz_specs', [])
    df = pd.DataFrame(data)

    primary_visual: Literal['table', 'chart', 'kpi'] = 'table'
    
    # KPI Mode: 1 row, 1 column
    if len(df) == 1 and len(df.columns) == 1:
        primary_visual = 'kpi'
    # Chart Mode: Multiple rows and viz_specs exist
    elif len(df) > 0 and viz_specs:
        primary_visual = 'chart'
    # Table Mode: fallback
    else:
        primary_visual = 'table'

    if not data or not viz_specs:
        return {'viz_specs': [], 'primary_visual': primary_visual}

    # Heuristic matching / refinement
    refined_specs = []
    for spec in viz_specs:
        encoding = spec.get('encoding', {}).copy()
        for axis in ['x', 'y', 'color']:
            if axis in encoding:
                field = encoding[axis].get('field')
                if field and field in df.columns:
                    if 'type' not in encoding[axis]:
                        field_lower = field.lower()
                        if any(k in field_lower for k in ['id', 'name', 'grade', 'status', 'email', 'date', 'major']):
                            encoding[axis]['type'] = 'nominal'
                        else:
                            encoding[axis]['type'] = 'quantitative'
                else:
                    encoding.pop(axis, None)

        refined_specs.append({
            'mark': {'type': spec.get('type', 'bar')},
            'encoding': encoding,
        })

    return {'viz_specs': refined_specs, 'primary_visual': primary_visual}


def final_analysis(state: AgentState) -> dict[str, Any]:
    """Generate final Vietnamese insights."""
    query = state.get('refined_query') or state.get('query')
    data = state.get('sql_results', [])
    sql_error = state.get('sql_error')

    if sql_error:
        err_msg = f'Xin lỗi, tôi không thể thực hiện truy vấn này sau nhiều lần thử. Lỗi: {sql_error}'
        return {
            'analysis': err_msg,
            'messages': [AIMessage(content=err_msg)]
        }

    if not data:
        msg = 'Không tìm thấy dữ liệu phù hợp với yêu cầu của bạn.'
        return {
            'analysis': msg,
            'messages': [AIMessage(content=msg)]
        }

    df = pd.DataFrame(data)
    df_sample = df.head(5).to_markdown()
    prompt = f"""Bạn là một chuyên gia phân tích dữ liệu. Hãy tóm tắt kết quả sau đây bằng tiếng Việt một cách dễ hiểu cho người dùng không rành kỹ thuật.

    Yêu cầu của người dùng: {query}
    Dữ liệu (5 dòng đầu):
    {df_sample}

    Tổng số dòng: {len(df)}

    Hãy cung cấp những hiểu biết sâu sắc và hành động có thể thực hiện được."""

    response = llm.invoke([
        SystemMessage(content='You are a helpful data analyst.'),
        HumanMessage(content=prompt),
    ])
    return {
        'analysis': response.content,
        'messages': [AIMessage(content=str(response.content))],
    }


def tts_generation(state: AgentState) -> dict[str, Any]:
    """Generate TTS audio from analysis."""
    analysis = state.get('analysis')
    if not analysis:
        return {'audio_base64': None}
    
    try:
        audio_fp = text2speech(analysis)
        if audio_fp:
            b64 = base64.b64encode(audio_fp.read()).decode()
            return {'audio_base64': b64}
        return {'audio_base64': None}
    except Exception as e:
        print(f"TTS Node Error: {str(e)}")
        return {'audio_base64': None}


def after_execute_router(
    state: AgentState,
) -> Literal['text_to_sql', 'viz_generation']:
    """Route after SQL execution."""
    if state.get('sql_error') and state.get('retry_count', 0) < 3:
        return 'text_to_sql'
    return 'viz_generation'


# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node('query_refinement', query_refinement)
workflow.add_node('text_to_sql', text_to_sql)
workflow.add_node('execute_sql', execute_sql)
workflow.add_node('viz_generation', viz_generation)
workflow.add_node('final_analysis', final_analysis)
workflow.add_node('tts_generation', tts_generation)

workflow.set_entry_point('query_refinement')
workflow.add_edge('query_refinement', 'text_to_sql')
workflow.add_edge('text_to_sql', 'execute_sql')

# Branching after execution: Viz and Analysis can start in parallel
workflow.add_conditional_edges(
    'execute_sql',
    after_execute_router,
    {
        'text_to_sql': 'text_to_sql', 
        'viz_generation': 'viz_generation'
    },
)

# Parallel path 1: Visualization
workflow.add_edge('viz_generation', END)

# Parallel path 2: Analysis -> TTS
workflow.add_edge('execute_sql', 'final_analysis')
workflow.add_edge('final_analysis', 'tts_generation')
workflow.add_edge('tts_generation', END)

# Compile
checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

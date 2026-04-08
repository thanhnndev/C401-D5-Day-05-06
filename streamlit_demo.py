from __future__ import annotations

import uuid

import pandas as pd
import streamlit as st
from streamlit_mic_recorder import mic_recorder

from src.graph import graph
from src.pipeline import decode_audio, speech2text


def render_custom_player(b64_audio: str):
    """Renders a custom-styled HTML5 audio player."""
    st.markdown(f"""
        <style>
            .audio-container {{ 
                background: #1E1E1E; 
                padding: 15px; 
                border-radius: 15px; 
                border: 1px solid #333;
                margin-bottom: 20px;
                display: flex;
                justify-content: center;
            }}
            audio {{
                width: 100%;
                filter: invert(100%) hue-rotate(180deg) brightness(1.5);
            }}
        </style>
        <div class="audio-container">
            <audio controls><source src="data:audio/mp3;base64,{b64_audio}"></audio>
        </div>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title='Voice Query Assistant',
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    st.title('🎙️ Voice Query Assistant')

    # Thread ID for persistence
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # Init history
    st.session_state.setdefault('history', [])

    col_chat_main, _ = st.columns([4, 1], gap='small')

    with col_chat_main:
        col_chat, col_voice_btn = st.columns([8, 1], gap='small')
        with col_voice_btn:
            audio_raw = mic_recorder(
                start_prompt='🎤',
                stop_prompt='🛑',
                key='audio_recorder',
            )
        with col_chat:
            user_text_input = st.chat_input('Hỏi bất cứ điều gì về dữ liệu của bạn...')

    user_query = None
    if user_text_input:
        user_query = user_text_input
    elif audio_raw:
        audio_fp = decode_audio(audio_raw)
        if audio_fp:
            with st.spinner('Đang chuyển giọng nói thành văn bản...'):
                user_query = speech2text(audio_fp)

    if not user_query:
        st.info("Hãy đặt câu hỏi bằng văn bản hoặc giọng nói để bắt đầu.")
        st.markdown('---')
        st.caption('VIN - AI20K - Team007')
        return

    st.markdown('---')
    res_col1, res_col2 = st.columns([2, 3], gap='large')

    with res_col1:
        st.subheader("💡 Phân tích")
        analysis_container = st.empty()
        audio_container = st.empty()

    with res_col2:
        st.subheader("📊 Kết quả")
        viz_container = st.empty()

    # Run LangGraph pipeline
    config = {'configurable': {'thread_id': st.session_state.thread_id}}
    input_data = {'query': user_query, 'retry_count': 0}

    with st.status('Đang xử lý...') as status:
        for step in graph.stream(input_data, config=config):
            # Update status message
            if 'query_refinement' in step:
                status.update(label='🔍 Đang tinh chỉnh câu hỏi...')
            elif 'text_to_sql' in step:
                status.update(label='💻 Đang tạo mã SQL...')
            elif 'execute_sql' in step:
                sql_data = step['execute_sql']
                if sql_data.get('sql_error'):
                    status.update(
                        label=f"⚠️ Lỗi SQL, đang thử lại (Lần {sql_data.get('retry_count')})...",
                        state='running',
                    )
                else:
                    status.update(label='⚙️ Đang thực thi truy vấn...')
            
            # Incremental Rendering
            elif 'viz_generation' in step:
                status.update(label='📊 Đang chuẩn bị biểu đồ...')
                viz_data = step['viz_generation']
                # We need the current results from the graph state
                current_state = graph.get_state(config).values
                df_result = pd.DataFrame(current_state.get('sql_results', []))
                
                with viz_container.container():
                    p_viz = viz_data.get('primary_visual', 'table')
                    specs = viz_data.get('viz_specs', [])
                    if p_viz == 'kpi' and not df_result.empty:
                        st.metric(label=df_result.columns[0], value=df_result.iloc[0, 0])
                    elif p_viz == 'chart' and specs:
                        for spec in specs:
                            st.vega_lite_chart(df_result, spec, use_container_width=True)
                        with st.expander("Xem bảng dữ liệu chi tiết"):
                            st.dataframe(df_result, use_container_width=True)
                    else:
                        st.dataframe(df_result, use_container_width=True)

            elif 'final_analysis' in step:
                status.update(label='💡 Đang phân tích kết quả...')
                analysis_text = step['final_analysis'].get('analysis', '')
                analysis_container.markdown(analysis_text)

            elif 'tts_generation' in step:
                status.update(label='🔊 Đang tạo giọng nói...')
                audio_b64 = step['tts_generation'].get('audio_base64')
                if audio_b64:
                    with audio_container:
                        render_custom_player(audio_b64)

        status.update(label='Hoàn tất!', state='complete')

    # Final result safety check & History
    full_state = graph.get_state(config).values
    insight = full_state.get('analysis', '')
    chart_specs = full_state.get('viz_specs', [])

    # History in sidebar
    with st.sidebar, st.expander('Lịch sử truy vấn', expanded=True):
        for q, insight_hist, _ in st.session_state.history[-5:]:
            st.caption(f'**Q:** {q}')
            st.caption(insight_hist[:100] + '...')
            st.divider()

    # Save to history (only if new query)
    if not st.session_state.history or st.session_state.history[-1][0] != user_query:
        st.session_state.history.append((
            user_query,
            insight,
            len(chart_specs),
        ))

    st.markdown('---')
    st.caption('VIN - AI20K - Team007')


if __name__ == '__main__':
    main()

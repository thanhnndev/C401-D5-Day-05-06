from __future__ import annotations

import uuid

import pandas as pd
import streamlit as st
from streamlit_mic_recorder import mic_recorder

from src.graph import graph
from src.pipeline import decode_audio, speech2text
from src.ui.renderer import StreamlitRenderer


def inject_custom_css():
    """Injects custom CSS for professional styling."""
    st.markdown("""
        <style>
            /* Make active tab more prominent */
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: transparent;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            .stTabs [aria-selected="true"] {
                background-color: rgba(255, 255, 255, 0.05);
                border-bottom: 2px solid #ff4b4b !important;
            }
            /* Add some padding to tab content */
            .stTabs [data-baseweb="tab-panel"] {
                padding-top: 20px;
            }
            /* Status bar styling */
            div[data-testid="stStatusWidget"] {
                margin-top: -15px;
                margin-bottom: 15px;
            }
        </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title='Query Assistant',
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    inject_custom_css()
    st.title('Query Assistant')

    # Thread ID for persistence
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # Init history and last results
    st.session_state.setdefault('history', [])
    st.session_state.setdefault('last_results', {
        'analysis': None,
        'audio_b64': None,
        'primary_visual': None,
        'viz_specs': None,
        'df_result': None
    })

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

    # Status container right below search bar
    status_container = st.empty()

    st.markdown('---')
    
    # Initialize Renderer
    renderer = StreamlitRenderer()

    # If no new query, try to show last results
    if not user_query:
        last = st.session_state.last_results
        if last['analysis']:
            renderer.update_insights(last['analysis'], last['audio_b64'])
        if last['df_result'] is not None:
            renderer.update_visualizations(last['primary_visual'], last['viz_specs'], last['df_result'])
            renderer.update_table(last['df_result'])
        
        if not last['analysis'] and last['df_result'] is None:
            st.info("Hãy đặt câu hỏi bằng văn bản hoặc giọng nói để bắt đầu.")
        
        st.markdown('---')
        st.caption('VIN - AI20K - Team007')
    else:
        # Reset last results for new query
        st.session_state.last_results = {
            'analysis': None,
            'audio_b64': None,
            'primary_visual': None,
            'viz_specs': None,
            'df_result': None
        }

        # Run LangGraph pipeline
        config = {'configurable': {'thread_id': st.session_state.thread_id}}
        input_data = {'query': user_query, 'retry_count': 0}

        with status_container:
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
                    
                    # Incremental Rendering via Renderer
                    elif 'viz_generation' in step:
                        status.update(label='📊 Đang chuẩn bị biểu đồ...')
                        viz_data = step['viz_generation']
                        current_state = graph.get_state(config).values
                        df_result = pd.DataFrame(current_state.get('sql_results', []))
                        
                        p_viz = viz_data.get('primary_visual', 'table')
                        specs = viz_data.get('viz_specs', [])
                        
                        renderer.update_visualizations(p_viz, specs, df_result)
                        renderer.update_table(df_result)
                        
                        # Cache results
                        st.session_state.last_results['primary_visual'] = p_viz
                        st.session_state.last_results['viz_specs'] = specs
                        st.session_state.last_results['df_result'] = df_result

                    elif 'final_analysis' in step:
                        status.update(label='💡 Đang phân tích kết quả...')
                        analysis_text = step['final_analysis'].get('analysis', '')
                        renderer.update_insights(analysis_text)
                        st.session_state.last_results['analysis'] = analysis_text

                    elif 'tts_generation' in step:
                        status.update(label='🔊 Đang tạo giọng nói...')
                        audio_b64 = step['tts_generation'].get('audio_base64')
                        if audio_b64:
                            renderer.update_insights(st.session_state.last_results['analysis'], audio_b64)
                            st.session_state.last_results['audio_b64'] = audio_b64

                status.update(label='Hoàn tất!', state='complete')

        # Final result safety check & History
        full_state = graph.get_state(config).values
        insight = full_state.get('analysis', '')
        chart_specs = full_state.get('viz_specs', [])

        # Save to history (only if new query)
        if not st.session_state.history or st.session_state.history[-1][0] != user_query:
            st.session_state.history.append((
                user_query,
                insight,
                len(chart_specs),
            ))

        st.markdown('---')
        st.caption('VIN - AI20K - Team007')

    # History in sidebar (always show if not empty)
    if st.session_state.history:
        with st.sidebar, st.expander('Lịch sử truy vấn', expanded=True):
            for q, insight_hist, _ in st.session_state.history[-5:]:
                st.caption(f'**Q:** {q}')
                st.caption(insight_hist[:100] + '...')
                st.divider()


if __name__ == '__main__':
    main()

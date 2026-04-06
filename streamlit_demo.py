import io
import base64

import streamlit as st
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder

from src.pipeline import run_pipeline, text2speech


def render_audio_text(audio_fp: io.BytesIO, llm_insight: str):
    audio_fp.seek(0)
    b64_audio = base64.b64encode(audio_fp.read()).decode()

    html_content = f"""
                        <div style="
                            font-family: sans-serif;
                            display: flex;
                            flex-direction: column;
                            height: 450px;
                            border-radius: 10px;
                            overflow: hidden;
                        ">
                            <audio id="tts_audio"
                                onended="
                                    document.getElementById('tts_icon').textContent = '🔊';
                                    var btn = document.getElementById('tts_btn');
                                    btn.style.background = 'linear-gradient(135deg, #FF6B6B, #FF4B4B)';
                                    btn.style.boxShadow = '0 4px 15px rgba(255,75,75,0.4)';
                                ">
                                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                            </audio>

                            <!-- Vung text cuon -->
                            <div style="
                                flex: 1;
                                overflow-y: auto;
                                font-size: 17px;
                                line-height: 1.8;
                                text-align: justify;
                                padding: 16px 18px;
                                color: #1a1a1a;
                            ">
                                {llm_insight}
                            </div>

                            <!-- Footer co dinh chua button -->
                            <div style="
                                flex-shrink: 0;
                                height: 56px;
                                background: #f9f9f9;
                                border-top: 1px solid #eeeeee;
                                display: flex;
                                align-items: center;
                                justify-content: flex-end;
                                padding: 0 16px;
                            ">
                                <button id="tts_btn"
                                    onclick="
                                        var audio = document.getElementById('tts_audio');
                                        var btn = document.getElementById('tts_btn');
                                        var icon = document.getElementById('tts_icon');
                                        if (audio.paused) {{
                                            audio.play();
                                            icon.textContent = '⏹';
                                            btn.style.background = 'linear-gradient(135deg, #e05252, #c0392b)';
                                            btn.style.boxShadow = '0 4px 15px rgba(192,57,43,0.5)';
                                        }} else {{
                                            audio.pause();
                                            audio.currentTime = 0;
                                            icon.textContent = '🔊';
                                            btn.style.background = 'linear-gradient(135deg, #FF6B6B, #FF4B4B)';
                                            btn.style.boxShadow = '0 4px 15px rgba(255,75,75,0.4)';
                                        }}
                                    "
                                    style="
                                        width: 40px;
                                        height: 40px;
                                        border-radius: 50%;
                                        border: none;
                                        background: linear-gradient(135deg, #FF6B6B, #FF4B4B);
                                        color: white;
                                        font-size: 17px;
                                        cursor: pointer;
                                        box-shadow: 0 4px 15px rgba(255,75,75,0.4);
                                        transition: transform 0.15s ease, box-shadow 0.15s ease;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                    "
                                    onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0 6px 20px rgba(255,75,75,0.55)';"
                                    onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 15px rgba(255,75,75,0.4)';"
                                >
                                    <span id="tts_icon">🔊</span>
                                </button>
                            </div>
                        </div>
                    """
    components.html(html_content, height=460, scrolling=False)


def voice_query():
    st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            border-radius: 50px;
            font-size: 20px;
            padding: 8px 16px;
            border: 2px solid #FF4B4B;
            background-color: transparent;
            color: #FF4B4B;
            transition: all 0.2s ease;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #FF4B4B;
            color: white;
        }
        </style>
        <div style="margin-top: 4px;"></div>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title='Voice Query Assistant', layout='wide')
    st.title('Voice Query Assistant')

    col_chat_main, col_voice_panel = st.columns([4, 1], gap='small')

    with col_chat_main:
        col_chat, col_voice_btn = st.columns([8, 1], gap='small')
        with col_voice_btn:
            voice_query()
            audio_raw = mic_recorder(
                start_prompt='Start',
                stop_prompt='Stop',
                key='audio_recorder',
            )
        with col_chat:
            user_text_input = st.chat_input('Ask anything about your data...')

    result = run_pipeline(user_query=user_text_input, audio_raw=audio_raw)

    if result is None:
        st.markdown('---')
        st.caption('VIN - AI20K - Team007')
        return

    audio_fp = text2speech(result['insight'])

    st.markdown('---')
    res_col1, res_col2 = st.columns([1.2, 1], gap='large')

    with res_col1:
        with st.container(border=True):
            render_audio_text(audio_fp, result['insight'])

    with res_col2:
        if result['chart']:
            with st.container(border=True):
                st.vega_lite_chart(
                    data=result['data'],
                    spec=result['chart'],
                    use_container_width=True,
                )

    st.markdown('---')
    st.caption('VIN - AI20K - Team007')


if __name__ == '__main__':
    main()

from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
from gtts import gTTS

import io
import json
import re
import base64
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

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

                            <!-- Vùng text cuộn -->
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

                            <!-- Footer cố định chứa button -->
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

def decode_audio(audio_raw: dict) -> io.BytesIO | None:
    if not audio_raw: return None
    try:
        audio_bytes = audio_raw['bytes']
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        mp3_fp = io.BytesIO()
        audio_segment.export(mp3_fp, format="mp3", bitrate="128k")
        mp3_fp.seek(0)
        return mp3_fp
    except Exception as e:
        st.error(f"Audio processing error: {e}")
        return None

def speech2text(audio_data: io.BytesIO) -> str:
    """
        Sound processed (func decode_audio) -> model (Whisper) -> Text
    """
    if not audio_data: return None
    response_from_model = "Danh sách 5 sinh viên có kết quả học tập thấp nhất trong tuần đầu tiên"

    return response_from_model

def text2sql_dbquery(user_query: str) -> str:
    """
        Text from Model (speech2text) -> sql query (model text2sql) -> query database
    """
    queried_data = pd.DataFrame({
        "Sinh viên": ["Hải Đặng", "Minh Hà", "Đức An", "Quang Hiển"],
        "Điểm TB": [2.1, 2.3, 2.8, 3.1]
    }) # mô phỏng data được truy vấn

    return queried_data
def data_visualization(queried_data):
    """
        Data (func text2sql) -> Vega-Lite JSON
        Convert output của model sang format Vega-Lite JSON
        Prompt mẫu: "Hãy tạo một cấu hình Vega-Lite JSON để vẽ biểu đồ cho dữ liệu sau {queried_data}
    """
    llm_response_json = """
                            {
                              "mark": {"type": "bar", "tooltip": true},
                              "encoding": {
                                "x": {"field": "Sinh viên", "type": "nominal", "axis": {"labelAngle": 0}},
                                "y": {"field": "Điểm TB", "type": "quantitative"},
                                "color": {"field": "Sinh viên", "type": "nominal"} 
                              }
                            }
                """ # mô phỏng output của model

    chart_spec = json.loads(llm_response_json)

    return chart_spec

def llm_analysis_data(user_query, queried_data):
    """
        data_query (func text2sql) -> LLM analysis data
    """
    response_text = (
        "Dựa trên dữ liệu queried_data của tuần đầu tiên, danh sách các sinh viên "
        "có kết quả học tập thấp nhất được xác định dựa trên cột “Điểm TB” theo thứ tự tăng dần. "
        "Cụ thể, sinh viên Hải Đặng có điểm trung bình 2.1, là mức thấp nhất trong nhóm và "
        "cho thấy cần được hỗ trợ học tập sớm để cải thiện kết quả trong các tuần tiếp theo. "
        "Tiếp theo là Minh Hà với điểm trung bình 2.3, vẫn thuộc nhóm điểm thấp và có thể "
        "gặp khó khăn trong việc nắm bắt kiến thức ban đầu của môn học. "
        "Sinh viên Đức An đạt điểm trung bình 2.8, mặc dù cao hơn hai trường hợp trước nhưng vẫn nằm "
        "trong nhóm có kết quả thấp khi so sánh với toàn bộ danh sách. "
        "Cuối cùng là Quang Hiển với điểm trung bình 3.1, là mức điểm cao nhất trong dữ liệu hiện có, "
        "tuy nhiên do số lượng sinh viên trong tập dữ liệu chỉ gồm bốn người nên Quang Hiển "
        "vẫn nằm trong danh sách các sinh viên có kết quả thấp nhất khi yêu cầu liệt kê tối đa năm người. "
        "Như vậy, do dữ liệu tuần đầu tiên chỉ ghi nhận bốn sinh viên nên danh sách 5 sinh viên"
        "có kết quả học tập thấp nhất thực tế chỉ bao gồm bốn người: Hải Đặng, Minh Hà, "
        "Đức An và Quang Hiển, được sắp xếp theo thứ tự điểm trung bình tăng dần. "
        "Kết quả này phản ánh rằng toàn bộ các sinh viên trong tập dữ liệu đều cần được "
        "theo dõi thêm trong những tuần tiếp theo, đặc biệt là hai trường hợp có điểm dưới "
        "2.5 nhằm đảm bảo tiến độ học tập chung và nâng cao chất lượng kết quả học tập trong "
        "các giai đoạn sau."
    )

    return response_text

def text2speech(text: str) -> io.BytesIO:
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    formatted = formatted.replace('\n', '<br>')
    tts = gTTS(text=formatted, lang='vi')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

def main():
    st.set_page_config(page_title="Voice Query Assistant", layout="wide")
    st.title(" Query Assistant")

    col_chat_main, col_voice = st.columns([4, 1], gap="small")

    with col_chat_main:
        col_chat, col_voice = st.columns([8, 1], gap="small")
        with col_voice:
            voice_query()
            audio_raw = mic_recorder(
                start_prompt="🎤",
                stop_prompt="⏹",
                use_container_width=True,
                key="audio_recorder"
            )

        with col_chat:
            user_text_input = st.chat_input(
                "Ask anything about your data... (Ctrl+Enter for new line)"
            )

    user_query = user_text_input
    if audio_raw and not user_text_input:
        mp3_data = decode_audio(audio_raw) # audio processing
        user_query = speech2text(mp3_data) # audio -> text (user query)

    if user_query:
        with st.spinner("DATA RETRIEVAL IN PROGRESS..."):
            df_result = text2sql_dbquery(user_query) # text -> sql query -> data
            llm_insight = llm_analysis_data(user_query, df_result) # data -> llm -> output
            audio_fp = text2speech(llm_insight) # text from 'llm_insight' -> audio_fb

            st.markdown("---")

            res_col1, res_col2 = st.columns([1.2, 1], gap="large")

            with res_col1:
                with st.container(border=True):
                    render_audio_text(audio_fp, llm_insight)

            with res_col2:
                chart_spec = data_visualization(df_result)
                # Display Visualization Data from 'df_result'
                with st.container(border=True):
                    st.vega_lite_chart(
                        data=df_result,
                        spec=chart_spec,
                        width='stretch',
                    )

    st.markdown("---")
    st.caption("VIN - AI20K - Team007")

if __name__ == "__main__":
    main()
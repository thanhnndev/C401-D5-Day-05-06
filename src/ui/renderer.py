import streamlit as st
import pandas as pd

class StreamlitRenderer:
    def __init__(self):
        # Create tabs
        self.t_insights, self.t_viz, self.t_table = st.tabs(["💡 Phân tích", "📊 Biểu đồ", "📋 Bảng dữ liệu"])
        
        # Initialize containers within tabs
        with self.t_insights:
            self.insight_container = st.empty()
            self.audio_container = st.empty()
            
        with self.t_viz:
            self.viz_container = st.empty()
            
        with self.t_table:
            self.table_container = st.empty()
            
        # Display initial empty states
        self.show_empty_states()

    def show_empty_states(self):
        """Displays friendly placeholder messages when tabs have no content."""
        with self.insight_container.container():
            st.info("Đang chờ phân tích...")
        with self.viz_container.container():
            st.info("Biểu đồ sẽ được hiển thị tại đây sau khi phân tích dữ liệu xong.")
        with self.table_container.container():
            st.info("Bảng dữ liệu chi tiết sẽ được hiển thị tại đây.")

    def render_custom_player(self, b64_audio: str):
        """Renders a compact custom-styled HTML5 audio player."""
        st.markdown(f"""
            <style>
                .audio-mini-container {{ 
                    background: rgba(30, 30, 30, 0.6); 
                    padding: 8px 15px; 
                    border-radius: 30px; 
                    border: 1px solid #444;
                    margin: 10px 0;
                    display: inline-flex;
                    align-items: center;
                    width: auto;
                    max-width: 300px;
                }}
                .audio-mini-container audio {{
                    height: 30px;
                    width: 200px;
                    filter: invert(100%) hue-rotate(180deg) brightness(1.5);
                }}
            </style>
            <div class="audio-mini-container">
                <audio controls><source src="data:audio/mp3;base64,{b64_audio}"></audio>
            </div>
        """, unsafe_allow_html=True)

    def update_insights(self, text: str, audio_b64: str = None):
        """Render Markdown analysis and the compact audio player in the 'Insights' tab."""
        with self.insight_container.container():
            st.markdown(text)
        if audio_b64:
            with self.audio_container.container():
                self.render_custom_player(audio_b64)

    def update_visualizations(self, p_viz: str, specs: list, df_result: pd.DataFrame):
        """Handle KPIs and Vega-Lite charts with reasonable sizing."""
        with self.viz_container.container():
            if df_result is None or df_result.empty:
                st.warning("Không có dữ liệu để hiển thị biểu đồ.")
                return

            if p_viz == 'kpi':
                st.metric(label=df_result.columns[0], value=df_result.iloc[0, 0])
            elif p_viz == 'chart' and specs:
                # Use columns to prevent charts from stretching too wide on large screens
                c1, c2 = st.columns([3, 1])
                with c1:
                    for spec in specs:
                        st.vega_lite_chart(df_result, spec, use_container_width=True)
            else:
                st.info("Không có cấu hình biểu đồ cụ thể. Xem tab 'Bảng dữ liệu' để biết chi tiết.")

    def update_table(self, df_result: pd.DataFrame):
        """Render the raw data table in the 'Tables' tab."""
        with self.table_container.container():
            if df_result is not None and not df_result.empty:
                st.dataframe(df_result, use_container_width=True)
            else:
                st.info("Đang chờ dữ liệu...")

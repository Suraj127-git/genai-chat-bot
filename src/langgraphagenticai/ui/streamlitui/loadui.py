import streamlit as st
import os

from src.langgraphagenticai.ui.uiconfigfile import Config
from src.langgraphagenticai.common.logger import logger

class LoadStreamlitUI:
    def __init__(self):
        self.config=Config()
        self.user_controls={}

    def load_streamlit_ui(self):
        try:
            logger.info("Initializing Streamlit UI")
            st.set_page_config(page_title= "🤖 " + self.config.get_page_title(), layout="wide")
            st.header("🤖 " + self.config.get_page_title())
            st.session_state.timeframe = ''
            st.session_state.IsFetchButtonClicked = False

            with st.sidebar:
                # Get options from config
                llm_options = self.config.get_llm_options()
                usecase_options = self.config.get_usecase_options()
                logger.info("Loaded configuration options successfully")

                # LLM selection
                self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)
                logger.info(f"Selected LLM: {self.user_controls['selected_llm']}")

                if self.user_controls["selected_llm"] == 'Groq':
                    model_options = self.config.get_groq_model_options()
                    self.user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
                    self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"]=st.text_input("API Key",type="password")
                    if not self.user_controls["GROQ_API_KEY"]:
                        logger.warning("Groq API key not provided")
                        st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")

                if self.user_controls["selected_llm"] == 'Ollama':
                    model_options = self.config.get_ollama_model_options()
                    self.user_controls["selected_ollama_model"] = st.selectbox("Select Model", model_options)
                    self.user_controls["OLLAMA_HOST"] = st.session_state["OLLAMA_HOST"]=st.text_input("Ollama Host", value="http://localhost:11434")
                    if not self.user_controls["OLLAMA_HOST"]:
                        logger.warning("Ollama host not provided")
                        st.warning("⚠️ Please enter your Ollama host address. Default is http://localhost:11434")

                self.user_controls["selected_usecase"]=st.selectbox("Select Usecases",usecase_options)
                logger.info(f"Selected usecase: {self.user_controls['selected_usecase']}")

                if self.user_controls["selected_usecase"] =="Chatbot With Web" or self.user_controls["selected_usecase"] =="AI News":
                    os.environ["TAVILY_API_KEY"]=self.user_controls["TAVILY_API_KEY"]=st.session_state["TAVILY_API_KEY"]=st.text_input("TAVILY API KEY",type="password")
                    if not self.user_controls["TAVILY_API_KEY"]:
                        logger.warning("Tavily API key not provided")
                        st.warning("⚠️ Please enter your TAVILY_API_KEY key to proceed. Don't have? refer : https://app.tavily.com/home")

                if self.user_controls['selected_usecase']=="AI News":
                    st.subheader("📰 AI News Explorer ")
                    with st.sidebar:
                        time_frame = st.selectbox(
                            "📅 Select Time Frame",
                            ["Daily", "Weekly", "Monthly"],
                            index=0
                        )
                    if st.button("🔍 Fetch Latest AI News", use_container_width=True):
                        logger.info(f"AI News fetch requested for timeframe: {time_frame}")
                        st.session_state.IsFetchButtonClicked = True
                        st.session_state.timeframe = time_frame

            logger.info("UI initialization completed successfully")
            return self.user_controls

        except Exception as e:
            error_msg = f"Error initializing UI: {str(e)}"
            logger.critical(error_msg)
            st.error(error_msg)
            return None
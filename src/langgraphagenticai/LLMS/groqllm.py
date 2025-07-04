import os
import streamlit as st
from langchain_groq import ChatGroq
from src.langgraphagenticai.common.logger import logger

class GroqLLM:
    def __init__(self,user_contols_input):
        self.user_controls_input=user_contols_input

    def get_llm_model(self):
        try:
            groq_api_key=self.user_controls_input["GROQ_API_KEY"]
            selected_groq_model=self.user_controls_input["selected_groq_model"]
            logger.info(f"Initializing Groq LLM with model: {selected_groq_model}")
            
            if groq_api_key=='' and os.environ["GROQ_API_KEY"] =='':
                logger.error("Groq API key not provided")
                st.error("Please Enter the Groq API KEY")

            llm=ChatGroq(api_key=groq_api_key,model=selected_groq_model)
            logger.info("Groq LLM initialized successfully")

        except Exception as e:
            logger.critical(f"Failed to initialize Groq LLM: {str(e)}")
            raise ValueError(f"Error occurred while initializing Groq LLM: {e}")
        return llm
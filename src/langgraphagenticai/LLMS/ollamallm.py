# src/langgraphagenticai/LLMS/ollamallm.py

import os
import streamlit as st
from langchain_community.chat_models import ChatOllama
from src.langgraphagenticai.common.logger import logger

class OllamaLLM:
    def __init__(self, user_contols_input):
        self.user_controls_input = user_contols_input

    def get_llm_model(self):
        try:
            selected_model = self.user_controls_input.get("selected_ollama_model", "llama3.2:1b")  # default: llama3
            logger.info(f"Initializing Ollama LLM with model: {selected_model}")

            llm = ChatOllama(model=selected_model)
            logger.info("Ollama LLM initialized successfully")

        except Exception as e:
            logger.critical(f"Failed to initialize Ollama LLM: {str(e)}")
            raise ValueError(f"Error occurred while initializing Ollama LLM: {e}")
        
        return llm

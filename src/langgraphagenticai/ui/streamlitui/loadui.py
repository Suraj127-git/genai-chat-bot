import streamlit as st
from typing import Dict, Any, Optional
from src.langgraphagenticai.common.logger import logger

class LoadStreamlitUI:
    """
    Enhanced UI loader with vector database management features
    """
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'IsFetchButtonClicked' not in st.session_state:
            st.session_state.IsFetchButtonClicked = False
        if 'timeframe' not in st.session_state:
            st.session_state.timeframe = ""
        if 'vector_db_enabled' not in st.session_state:
            st.session_state.vector_db_enabled = True
    
    def load_streamlit_ui(self) -> Optional[Dict[str, Any]]:
        """
        Load the enhanced Streamlit UI with vector database options
        """
        st.title("🤖 LangGraph AgenticAI with Vector Database")
        st.markdown("---")
        
        # Main configuration columns
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.subheader("🛠️ LLM Configuration")
            
            # LLM Selection
            selected_llm = st.selectbox(
                "Select LLM Provider",
                options=["Groq", "Ollama"],
                index=0,
                help="Choose your preferred LLM provider"
            )
            
            # Model Selection based on LLM
            if selected_llm == "Ollama":
                selected_model = st.selectbox(
                    "Select Ollama Model",
                    options=[
                        "llama3.2:1b",
                        "llama3.2:3b", 
                        "llama3:8b",
                        "mistral:7b",
                        "codellama:13b"
                    ],
                    index=0,
                    help="Choose your Ollama model"
                )
            else:
                selected_model = st.selectbox(
                    "Select Groq Model",
                    options=[
                        "llama3-8b-8192",
                        "llama3-70b-8192",
                        "mixtral-8x7b-32768",
                        "gemma-7b-it"
                    ],
                    index=0,
                    help="Choose your Groq model"
                )
        
        with col2:
            st.subheader("🎯 Use Case Selection")
            
            # Use Case Selection
            selected_usecase = st.selectbox(
                "Select Use Case",
                options=[
                    "Basic Chatbot",
                    "Chatbot With Web", 
                    "AI News"
                ],
                index=0,
                help="Choose the functionality you want to use"
            )
            
            # Vector Database Toggle
            st.session_state.vector_db_enabled = st.checkbox(
                "Enable Vector Database",
                value=True,
                help="Use vector database for caching and similarity search"
            )
            
            # Show use case description
            use_case_descriptions = {
                "Basic Chatbot": "💬 Simple chat interface with vector-enhanced responses",
                "Chatbot With Web": "🌐 Chat with web search capabilities",
                "AI News": "📰 AI news aggregation and summarization with caching"
            }
            
            st.info(use_case_descriptions.get(selected_usecase, ""))
        
        with col3:
            st.subheader("⚙️ Advanced Settings")
            
            # Temperature setting
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Controls randomness in responses"
            )
            
            # Max tokens
            max_tokens = st.slider(
                "Max Tokens",
                min_value=100,
                max_value=4000,
                value=1000,
                step=100,
                help="Maximum tokens in response"
            )
            
            # Vector search settings
            if st.session_state.vector_db_enabled:
                st.markdown("**Vector Search Settings**")
                
                vector_search_limit = st.slider(
                    "Search Results Limit",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="Number of similar questions to retrieve"
                )
                
                similarity_threshold = st.slider(
                    "Similarity Threshold",
                    min_value=0.5,
                    max_value=0.95,
                    value=0.8,
                    step=0.05,
                    help="Minimum similarity to use cached response"
                )
        
        # AI News specific settings
        if selected_usecase == "AI News":
            st.markdown("---")
            st.subheader("📰 AI News Settings")
            
            col_news1, col_news2 = st.columns(2)
            
            with col_news1:
                timeframe = st.selectbox(
                    "Select News Timeframe",
                    options=[
                        "last 24 hours",
                        "last 3 days", 
                        "last week",
                        "last month"
                    ],
                    index=0,
                    help="Choose the timeframe for news aggregation"
                )
                
                fetch_button = st.button(
                    "🔄 Fetch AI News",
                    help="Fetch and summarize AI news for the selected timeframe"
                )
                
                if fetch_button:
                    st.session_state.IsFetchButtonClicked = True
                    st.session_state.timeframe = f"Get AI news from {timeframe}"
            
            with col_news2:
                # News source preferences
                news_sources = st.multiselect(
                    "Preferred News Sources",
                    options=[
                        "TechCrunch",
                        "Wired",
                        "MIT Technology Review",
                        "VentureBeat",
                        "The Verge",
                        "Ars Technica"
                    ],
                    default=["TechCrunch", "Wired"],
                    help="Select preferred news sources"
                )
                
                # Summary length
                summary_length = st.selectbox(
                    "Summary Length",
                    options=["Brief", "Detailed", "Comprehensive"],
                    index=1,
                    help="Choose the length of news summaries"
                )
        
        # Compile user input
        user_input = {
            "selected_llm": selected_llm,
            "selected_model": selected_model,
            "selected_usecase": selected_usecase,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "vector_db_enabled": st.session_state.vector_db_enabled,
        }
        
        # Add model-specific keys
        if selected_llm == "Ollama":
            user_input["selected_ollama_model"] = selected_model
        else:
            user_input["selected_groq_model"] = selected_model
        
        # Add vector search settings if enabled
        if st.session_state.vector_db_enabled:
            user_input.update({
                "vector_search_limit": vector_search_limit,
                "similarity_threshold": similarity_threshold
            })
        
        # Add AI News specific settings
        if selected_usecase == "AI News":
            user_input.update({
                "timeframe": timeframe,
                "news_sources": news_sources,
                "summary_length": summary_length
            })
        
        logger.info(f"UI Configuration: {user_input}")
        return user_input

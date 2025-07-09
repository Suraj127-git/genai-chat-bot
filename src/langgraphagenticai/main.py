import streamlit as st
import os
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.LLMS.ollamallm import OllamaLLM
from src.langgraphagenticai.graph.enhanced_graph_builder import EnhancedGraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit
from src.langgraphagenticai.common.logger import logger

def load_langgraph_agenticai_app():
    """
    Loads and runs the enhanced LangGraph AgenticAI application with Streamlit UI and Qdrant integration.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the enhanced graph with vector database capabilities, and displays the output.
    """
    
    # Initialize Streamlit page configuration
    st.set_page_config(
        page_title="LangGraph AgenticAI with Vector Database",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add vector database status in sidebar
    with st.sidebar:
        st.header("🗄️ Vector Database Status")
        
        # Check if Qdrant is available
        try:
            from src.langgraphagenticai.database.qdrant_manager import QdrantManager
            qdrant_test = QdrantManager()
            db_stats = qdrant_test.get_collection_stats()
            
            st.success("✅ Qdrant Connected")
            st.metric("Total Q&A Pairs", db_stats.get('total_points', 0))
            st.metric("Vector Dimensions", db_stats.get('vector_size', 0))
            
            # Add database management buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 View Stats"):
                    st.json(db_stats)
            with col2:
                if st.button("🗑️ Clear DB"):
                    if qdrant_test.clear_database():
                        st.success("Database cleared!")
                        st.rerun()
                    else:
                        st.error("Failed to clear database")
                        
        except Exception as e:
            st.error(f"❌ Qdrant Connection Failed: {str(e)}")
            st.info("💡 Make sure Qdrant is running on localhost:6333")
            
        st.divider()
    
    # Load main UI
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()
    
    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return
    
    # Add embedding model selection
    with st.expander("🔧 Advanced Settings"):
        embedding_model = st.selectbox(
            "Select Embedding Model",
            options=[
                "nomic-embed-text",
                "text-embedding-ada-002",
                "text-embedding-3-small",
                "llama3.2:1b"
            ],
            index=0,
            help="Choose the embedding model for vector similarity search"
        )
        
        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.5,
            max_value=0.95,
            value=0.8,
            step=0.05,
            help="Minimum similarity score to use cached responses"
        )
    
    # Text input for user message
    if st.session_state.get('IsFetchButtonClicked', False):
        user_message = st.session_state.get('timeframe', '')
    else:
        user_message = st.chat_input("Enter your message:")
    
    if user_message:
        # Display user message
        with st.chat_message("user"):
            st.write(user_message)
        
        try:
            # Configure The LLM's
            logger.info(f"User Input: {user_input}")
            
            if user_input.get("selected_llm") == "Ollama":
                obj_llm_config = OllamaLLM(user_contols_input=user_input)
            else:
                obj_llm_config = GroqLLM(user_contols_input=user_input)
            
            model = obj_llm_config.get_llm_model()
            
            if not model:
                st.error("Error: LLM model could not be initialized")
                return
            
            # Get use case
            usecase = user_input.get("selected_usecase")
            
            if not usecase:
                st.error("Error: No use case selected.")
                return
            
            # Initialize Enhanced Graph Builder with vector database
            with st.spinner("🚀 Initializing Enhanced Graph with Vector Database..."):
                enhanced_graph_builder = EnhancedGraphBuilder(
                    model=model,
                    embedding_model=embedding_model
                )
                
                # Set up the graph
                graph = enhanced_graph_builder.setup_graph(usecase)
                
                logger.info(f"Processing message: {user_message}")
                
                # Display result with enhanced functionality
                with st.chat_message("assistant"):
                    result_display = DisplayResultStreamlit(usecase, graph, user_message)
                    
                    # Add vector database context to the display
                    if hasattr(result_display, 'display_result_on_ui'):
                        result_display.display_result_on_ui()
                    else:
                        # Fallback display method
                        st.write("Processing your request...")
                        
                        # Run the graph
                        if usecase == "AI News":
                            initial_state = {
                                "messages": [user_message],
                                "user_message": user_message,
                                "usecase": usecase
                            }
                        else:
                            initial_state = {
                                "messages": [user_message],
                                "usecase": usecase
                            }
                        
                        # Execute the graph
                        result = graph.invoke(initial_state)
                        
                        # Display results based on use case
                        if usecase == "AI News":
                            if 'summary' in result:
                                st.markdown("### 📰 AI News Summary")
                                st.write(result['summary'])
                                
                                # Check if from cache
                                if result.get('from_cache'):
                                    st.info("🔄 This response was retrieved from vector database cache")
                                else:
                                    st.success("✨ Fresh news summary generated and cached")
                            
                            if 'saved_file' in result:
                                st.success(f"📁 Results saved to: {result['saved_file']}")
                                
                        else:
                            # For chatbot responses
                            if 'messages' in result:
                                response = result['messages']
                                if hasattr(response, 'content'):
                                    content = response.content
                                elif isinstance(response, list) and len(response) > 0:
                                    content = response[-1] if isinstance(response[-1], str) else str(response[-1])
                                else:
                                    content = str(response)
                                
                                st.write(content)
                                
                                # Check if response was from cache
                                if "*[This response was retrieved from previous similar questions]*" in content:
                                    st.info("🔄 Similar question found in database - response retrieved from cache")
                                else:
                                    st.success("✨ New response generated and cached for future use")
                
                # Update database stats in sidebar
                try:
                    updated_stats = enhanced_graph_builder.get_database_stats()
                    if updated_stats:
                        logger.info(f"Database updated: {updated_stats}")
                except Exception as e:
                    logger.warning(f"Could not update database stats: {e}")
                    
        except Exception as e:
            st.error(f"Error: Failed to process request - {str(e)}")
            logger.error(f"Error in main processing: {e}")
            
            # Show detailed error in expander
            with st.expander("🔍 Error Details"):
                st.code(str(e))
            
            return


def main():
    """
    Main entry point for the enhanced application
    """
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verify required environment variables
        required_vars = ["QDRANT_URL"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            st.warning(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
            st.info("Using default values. Check your .env file for optimal configuration.")
        
        # Load the application
        load_langgraph_agenticai_app()
        
    except Exception as e:
        st.error(f"Failed to start application: {str(e)}")
        logger.critical(f"Application startup failed: {e}")


if __name__ == "__main__":
    main()


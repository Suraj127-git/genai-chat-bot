import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json
from src.langgraphagenticai.common.logger import logger


class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        try:
            usecase = self.usecase
            graph = self.graph
            user_message = self.user_message
            logger.info(f"Displaying results for usecase: {usecase}")
            
            if usecase == "Basic Chatbot":
                logger.info("Processing Basic Chatbot interaction")
                
                # Display user message first
                with st.chat_message("user"):
                    st.write(user_message)
                
                # Process graph stream
                for event in graph.stream({'messages': ("user", user_message)}):
                    for value in event.values():
                        logger.debug(f"Processing value: {type(value)} - {value}")
                        
                        # Handle different message structures
                        messages = value.get("messages", [])
                        
                        # If messages is a single message object, convert to list
                        if isinstance(messages, str):
                            # Handle case where messages is a plain string
                            with st.chat_message("assistant"):
                                st.write(messages)
                        elif not isinstance(messages, list):
                            messages = [messages]
                        
                        # Process each message
                        for message in messages:
                            if isinstance(message, str):
                                # Handle plain string messages
                                with st.chat_message("assistant"):
                                    st.write(message)
                            elif hasattr(message, 'content') and message.content:
                                # Check message type and display accordingly
                                if isinstance(message, HumanMessage):
                                    # Skip user messages in stream as we already displayed it
                                    continue
                                elif isinstance(message, AIMessage):
                                    with st.chat_message("assistant"):
                                        st.write(message.content)
                                elif isinstance(message, ToolMessage):
                                    with st.chat_message("ai"):
                                        st.write("Tool Call:")
                                        st.write(message.content)
                            else:
                                # Handle case where message doesn't have content attribute
                                logger.warning(f"Message without content attribute: {type(message)} - {message}")
                                
                logger.info("Basic Chatbot response displayed successfully")

            elif usecase == "Chatbot With Web":
                logger.info("Processing Chatbot With Web interaction")
                initial_state = {"messages": [user_message]}
                res = graph.invoke(initial_state)
                
                for message in res['messages']:
                    if isinstance(message, HumanMessage):
                        with st.chat_message("user"):
                            st.write(message.content)
                    elif isinstance(message, ToolMessage):
                        with st.chat_message("ai"):
                            st.write("Tool Call Start")
                            st.write(message.content)
                            st.write("Tool Call End")
                    elif isinstance(message, AIMessage) and message.content:
                        with st.chat_message("assistant"):
                            st.write(message.content)
                            
                logger.info("Chatbot With Web response displayed successfully")

            elif usecase == "AI News":
                logger.info(f"Processing AI News request for frequency: {user_message}")
                frequency = self.user_message
                
                with st.spinner("Fetching and summarizing news... ⏳"):
                    result = graph.invoke({"messages": frequency})
                    
                    try:
                        AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
                        logger.info(f"Reading news summary from: {AI_NEWS_PATH}")
                        
                        with open(AI_NEWS_PATH, "r", encoding="utf-8") as file:
                            markdown_content = file.read()
                            
                        st.markdown(markdown_content, unsafe_allow_html=True)
                        logger.info("AI News summary displayed successfully")
                        
                    except FileNotFoundError:
                        error_msg = f"News Not Generated or File not found: {AI_NEWS_PATH}"
                        logger.error(error_msg)
                        st.error(error_msg)
                    except Exception as e:
                        error_msg = f"Error displaying AI News: {str(e)}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        
            else:
                error_msg = f"Invalid usecase: {usecase}"
                logger.error(error_msg)
                st.error(error_msg)
                
        except Exception as e:
            error_msg = f"Error in display_result_on_ui: {str(e)}"
            logger.critical(error_msg)
            st.error(error_msg)
            
    def display_result_on_ui_safe(self):
        """Alternative safer method with better error handling"""
        try:
            usecase = self.usecase
            graph = self.graph
            user_message = self.user_message
            logger.info(f"Displaying results for usecase: {usecase}")
            
            if usecase == "Basic Chatbot":
                logger.info("Processing Basic Chatbot interaction")
                
                # Display user message
                with st.chat_message("user"):
                    st.write(user_message)
                
                # Process graph stream with better error handling
                try:
                    for event in graph.stream({'messages': ("user", user_message)}):
                        for key, value in event.items():
                            logger.debug(f"Event key: {key}, value type: {type(value)}")
                            
                            # Handle different response structures
                            if isinstance(value, dict) and "messages" in value:
                                messages = value["messages"]
                                
                                # Handle different message types
                                if isinstance(messages, str):
                                    # Handle plain string response
                                    with st.chat_message("assistant"):
                                        st.write(messages)
                                elif isinstance(messages, list):
                                    # Multiple messages
                                    for msg in messages:
                                        self._display_single_message(msg)
                                else:
                                    # Single message object
                                    self._display_single_message(messages)
                            else:
                                logger.warning(f"Unexpected value structure: {type(value)} - {value}")
                                
                except Exception as stream_error:
                    logger.error(f"Error in stream processing: {stream_error}")
                    st.error(f"Error processing response: {stream_error}")
                    
                logger.info("Basic Chatbot response displayed successfully")

            elif usecase == "Chatbot With Web":
                logger.info("Processing Chatbot With Web interaction")
                initial_state = {"messages": [user_message]}
                res = graph.invoke(initial_state)
                
                for message in res['messages']:
                    self._display_single_message(message)
                    
                logger.info("Chatbot With Web response displayed successfully")

            elif usecase == "AI News":
                logger.info(f"Processing AI News request for frequency: {user_message}")
                frequency = self.user_message
                
                with st.spinner("Fetching and summarizing news... ⏳"):
                    result = graph.invoke({"messages": frequency})
                    
                    try:
                        AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
                        logger.info(f"Reading news summary from: {AI_NEWS_PATH}")
                        
                        with open(AI_NEWS_PATH, "r", encoding="utf-8") as file:
                            markdown_content = file.read()
                            
                        st.markdown(markdown_content, unsafe_allow_html=True)
                        logger.info("AI News summary displayed successfully")
                        
                    except FileNotFoundError:
                        error_msg = f"News Not Generated or File not found: {AI_NEWS_PATH}"
                        logger.error(error_msg)
                        st.error(error_msg)
                    except Exception as e:
                        error_msg = f"Error displaying AI News: {str(e)}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        
            else:
                error_msg = f"Invalid usecase: {usecase}"
                logger.error(error_msg)
                st.error(error_msg)
                
        except Exception as e:
            error_msg = f"Error in display_result_on_ui_safe: {str(e)}"
            logger.critical(error_msg)
            st.error(error_msg)
            
    def _display_single_message(self, message):
        """Helper method to display a single message"""
        try:
            if isinstance(message, str):
                # Handle plain string messages
                with st.chat_message("assistant"):
                    st.write(message)
            elif isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, ToolMessage):
                with st.chat_message("ai"):
                    st.write("Tool Call Start")
                    st.write(message.content)
                    st.write("Tool Call End")
            elif isinstance(message, AIMessage) and hasattr(message, 'content') and message.content:
                with st.chat_message("assistant"):
                    st.write(message.content)
            else:
                logger.warning(f"Unhandled message type: {type(message)} - {message}")
        except Exception as e:
            logger.error(f"Error displaying message: {e}")
            st.error(f"Error displaying message: {e}")
# src/langgraphagenticai/nodes/chatbot_with_Tool_node.py

from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.common.logger import logger
import json

class ChatbotWithToolNode:
    """
    Chatbot logic enhanced with tool integration.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        """
        Processes the input state and generates a response without tools.
        """
        logger.info(f"ChatbotWithToolNode processing state: {state}")
        user_input = state.get("messages", [""])[-1]
        llm_response = self.llm.invoke([{"role": "user", "content": user_input}])

        tools_response = f"Tool integration placeholder for: '{user_input}'"
        logger.info(f"ChatbotWithToolNode responses - LLM: {llm_response}, Tools: {tools_response}")
        return {"messages": [llm_response, tools_response]}
    
    def create_chatbot(self, tools):
        """
        Returns a chatbot node function that uses tools when available.
        """
        # 1) Try direct bind_tools if supported
        if hasattr(self.llm, "bind_tools"):
            try:
                llm_with_tools = self.llm.bind_tools(tools)
                logger.info("Bound tools directly to LLM via bind_tools().")

                def chatbot_node(state: State):
                    logger.info(f"ChatbotWithToolNode (bound) processing state: {state}")
                    response = llm_with_tools.invoke(state.get("messages", []))
                    return {"messages": [response]}

                return chatbot_node
            except Exception as e:
                logger.info(f"LLM.bind_tools() failed: {e}. Falling back to manual tool handling.")

        # 2) Manual tool handling approach
        def chatbot_node(state: State):
            user_input = state.get("messages", [""])[-1]
            logger.info(f"ChatbotWithToolNode processing: {user_input}")
            
            # Extract text content from message object if needed
            if hasattr(user_input, 'content'):
                input_text = user_input.content
            elif isinstance(user_input, dict) and 'content' in user_input:
                input_text = user_input['content']
            else:
                input_text = str(user_input)
            
            logger.info(f"Extracted input text: {input_text}")
            
            # Simple keyword-based tool detection
            search_keywords = [
                'latest', 'current', 'version', 'news', 'today', 'recent', 
                'what is', 'who is', 'how to', 'search', 'find', 'lookup',
                'php', 'python', 'javascript', 'technology'
            ]
            
            needs_search = any(keyword.lower() in input_text.lower() for keyword in search_keywords)
            
            if needs_search and tools:
                logger.info("Search needed, using tools...")
                try:
                    # Use the first available tool (assuming it's a search tool)
                    search_tool = tools[0]
                    logger.info(f"Using tool: {type(search_tool).__name__}")
                    
                    # Call the tool with the input
                    if hasattr(search_tool, 'invoke'):
                        search_result = search_tool.invoke(input_text)
                    elif hasattr(search_tool, 'run'):
                        search_result = search_tool.run(input_text)
                    else:
                        search_result = search_tool(input_text)
                    
                    logger.info(f"Tool result: {search_result}")
                    
                    # Create a context-aware prompt
                    context_prompt = f"""Based on the following search result, please answer the user's question: "{input_text}"

Search result: {search_result}

Please provide a clear and helpful answer based on this information."""
                    
                    # Get LLM response with context
                    response = self.llm.invoke([{"role": "user", "content": context_prompt}])
                    
                    # Extract response content
                    if hasattr(response, 'content'):
                        result = response.content
                    else:
                        result = str(response)
                    
                    logger.info(f"Final response: {result}")
                    return {"messages": [result]}
                    
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    # Fall back to direct LLM response
                    response = self.llm.invoke([{"role": "user", "content": input_text}])
                    if hasattr(response, 'content'):
                        return {"messages": [response.content]}
                    else:
                        return {"messages": [str(response)]}
            else:
                # Direct LLM response for non-search queries
                logger.info("Using direct LLM response...")
                try:
                    response = self.llm.invoke([{"role": "user", "content": input_text}])
                    if hasattr(response, 'content'):
                        return {"messages": [response.content]}
                    else:
                        return {"messages": [str(response)]}
                except Exception as e:
                    logger.error(f"LLM invocation failed: {e}")
                    return {"messages": [f"Error: {str(e)}"]}

        return chatbot_node
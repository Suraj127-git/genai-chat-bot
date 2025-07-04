from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.common.logger import logger

class BasicChatbotNode:
    """
    Basic Chatbot login implementation
    """
    def __init__(self,model):
        self.llm=model

    def process(self,state:State)->dict:
        """
        Processes the input state and generates a chatbot response.
        """
        logger.info(f"BasicChatbotNode processing state: {state}")
        return {"messages":self.llm.invoke(state['messages'])}


from typing import List, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.state import AgentState

class BaseAgent:
    def __init__(self, name: str, model: BaseChatModel, tools: List[BaseTool] = []):
        self.name = name
        self.model = model
        self.tools = tools
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are {name}. {system_prompt}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        if self.tools:
            self.model = self.model.bind_tools(self.tools)

    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Invokes the LLM with the current state and returns the updated state keys.
        This is a simplified implementation. In a real scenario, we would handle tool calling loops.
        """
        # For now, we just pass the last message to the model
        # In a real LangGraph node, we might want to format the state into a prompt
        
        # This is a placeholder implementation to be overridden or extended by specific agents
        # or to be used as a generic agent runner.
        
        # Construct the prompt with the system prompt (which should be set by the subclass)
        # and the messages from the state.
        chain = self.prompt | self.model
        response = chain.invoke({
            "name": self.name,
            "system_prompt": getattr(self, "system_prompt", "You are a helpful AI assistant."),
            "messages": state["messages"]
        })
        
        return {"messages": [response]}

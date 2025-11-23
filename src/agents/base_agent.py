from typing import List, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.state import AgentState

class BaseAgent:
    def __init__(self, name: str, model: BaseChatModel, tools: List[BaseTool] = [], callback=None):
        self.name = name
        self.model = model
        self.tools = tools
        self.callback = callback
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are {name}. {system_prompt}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        if self.tools:
            self.model = self.model.bind_tools(self.tools)

    def log(self, message: str, type: str = "info", data: Any = None):
        """Log a message to console and callback."""
        print(f"[{self.name}] {message}")
        if self.callback:
            # If callback is async, we might need to handle it, but for now assume sync or fire-and-forget
            # In main.py we passed manager.broadcast which is async. 
            # We might need to run it in event loop if it's a coroutine.
            # But here we just call it.
            try:
                import asyncio
                from datetime import datetime
                payload = {
                    "agent": self.name,
                    "message": message,
                    "type": type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                if asyncio.iscoroutinefunction(self.callback):
                    # We are likely in a sync context (agent run), so we can't await easily.
                    # We can try to create a task if loop is running.
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(self.callback(payload))
                    except RuntimeError:
                        # No running loop
                        pass
                else:
                    self.callback(payload)
            except Exception as e:
                print(f"Callback failed: {e}")

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

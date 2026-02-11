from src.langgraphagenticai.state.state import State
from langchain_core.messages import ToolMessage
class NewsSummarizerNode:
    def __init__(self,model):
        self.llm=model
    
    def fetch_news(self,tool,frequency,tate):
        """
        Creates a node function that fetches AI news using the Tavily search tool.
        Returns a callable node function that LangGraph can execute
        """
        def _fetch_node(state: State):
            query = f"fetch the most important and relevant ai news within {frequency} range till today"
            news = tool[0].invoke(query)  # tool is a list, so use tool[0]
            return {
                "messages": [
                    ToolMessage(
                        content=str(news),
                        name="news_search",
                        tool_call_id="news_fetch_001"  # Add this required field
                    )
                ]
            }
        return _fetch_node
    
    def summarizer(self,state):
        """
        Summarizes news content from the state messages.
        Returns:
            Dictionary with summarized news message
        """
        news_content = "" 
        for message in state["messages"]:
            if isinstance(message, ToolMessage):
                news_content += message.content + "\n"
        
        prompt = f"""Summarize and organize the following news content in proper markdown format 
        with dates mentioned in order and valuable insights:
        
        {news_content}
        """
        return {"messages":[self.llm.invoke(prompt)]}
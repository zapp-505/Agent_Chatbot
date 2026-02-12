from langgraph.graph import StateGraph
from src.langgraphagenticai.state.state import State
from langgraph.graph import START,END
from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from langgraph.prebuilt import tools_condition, ToolNode
from src.langgraphagenticai.tools.search_tool import search_tool,create_tool_node
from src.langgraphagenticai.nodes.chatbot_with_tool_node import ChatbotWithToolNode
from src.langgraphagenticai.nodes.news_summarizer_node import NewsSummarizerNode

class GraphBuilder:
    def __init__(self,model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        self.basic_chatbot_node=BasicChatbotNode(self.llm)

        self.graph_builder.add_node("chatbot",self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)

    def agent_with_tools_build_graph(self):
        """
        Builds an advanced chatbot graph using LangGraph with tool integration.
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        tool=search_tool()
        tool_node = create_tool_node(tool)

        self.agent_with_tools_node = ChatbotWithToolNode(self.llm)
        chatbot_node= self.agent_with_tools_node.create_chatbot(tool)
        
        self.graph_builder.add_node("chatbot",chatbot_node)
        self.graph_builder.add_node("tools",tool_node)

        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot",tools_condition)
        self.graph_builder.add_edge("tools","chatbot")
        self.graph_builder.add_edge("chatbot",END)

    def news_summarizer_build_graph(self, frequency):
        """
        Builds the AI news summarizer graph with fetch and summarize nodes.
        
        Args:
            frequency (str): Time frame for news (daily, weekly, monthly, year)
        """
        self.news_node = NewsSummarizerNode(self.llm)  
        fetch_node = self.news_node.fetch_news(frequency) 
        
        self.graph_builder.add_node("news", fetch_node)
        self.graph_builder.add_node("summarizer", self.news_node.summarizer)
        self.graph_builder.add_edge(START, "news")
        self.graph_builder.add_edge("news", "summarizer")
        self.graph_builder.add_edge("summarizer", END)

    def setup_graph(self,usecase:str,frequency):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        
        elif usecase == "Chatbot with Tool":
            self.agent_with_tools_build_graph()
        
        elif usecase == "AI news":
           
            self.news_summarizer_build_graph(frequency) 
        
        else:
            raise ValueError(f"Unknown use case: {usecase}")

        return self.graph_builder.compile()
    
    """from src.langgraphagenticai.state.state import State
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
    """
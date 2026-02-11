from langgraph.graph import StateGraph
from src.langgraphagenticai.state.state import State
from langgraph.graph import START,END
from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from langgraph.prebuilt import tools_condition, ToolNode
from src.langgraphagenticai.tools.search_tool import search_tool,create_tool_node
from src.langgraphagenticai.nodes.chatbot_with_tool_node import ChatbotWithToolNode

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

    def news_summarizer_build_graph(self):
        tool = search_tool()
        tool_node = create_tool_node(tool)

        

    def setup_graph(self,usecase:str):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        
        elif usecase == "Chatbot with Tool":
            self.agent_with_tools_build_graph()
        
        elif usecase == "AI news":
            # TODO: Implement AI news use case
            self.basic_chatbot_build_graph()  # Fallback to basic chatbot for now
        
        else:
            raise ValueError(f"Unknown use case: {usecase}")

        return self.graph_builder.compile()
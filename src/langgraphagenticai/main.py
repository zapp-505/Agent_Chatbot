import streamlit as st
import os
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit

def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the graph based on the selected use case, and displays the output while 
    implementing exception handling for robustness.
    """

    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    # Set Tavily API key if provided and not empty
    tavily_key = user_input.get("TAVILY_API_KEY", "").strip()
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
    
    user_message = st.chat_input("Enter your message:")

    if user_message:
        obj_llm_config=GroqLLM(user_controls_input=user_input)
        model=obj_llm_config.get_llm_model()

        if not model:
            st.error("LLM could not be intialized")
            return
        
        usecase=user_input.get("selected_usecase")
        frequency = user_input.get("news_option")
        if not usecase:
                st.error("Error: No use case selected.")
                return
        
        # Validate Tavily API key for tool-based use cases
        if usecase == "Chatbot with Tool":
            if not os.environ.get("TAVILY_API_KEY"):
                st.error("⚠️ Tavily API key is required for 'Chatbot with Tool'. Please enter it in the sidebar.")
                return
        
             
        graph_builder= GraphBuilder(model)
        try:
             graph=graph_builder.setup_graph(usecase,frequency)
             print(user_message)
             DisplayResultStreamlit(usecase,graph,user_message).display_result_on_ui()
        except Exception as e:
                 st.error(f"Error: Graph set up failed- {e}")
                 return

import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json


class DisplayResultStreamlit:
    def __init__(self,usecase,graph,user_message):
        self.usecase= usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase= self.usecase
        graph = self.graph
        user_message = self.user_message
        
        # Initialize chat history in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display existing chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Display current user message
        with st.chat_message("user"):
            st.write(user_message)
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        if usecase == "Basic Chatbot" or usecase == "AI news":
            '''returns an iterator of events. Each event is a dictionary where keys are node names (e.g., from the graph's execution) and values are state updates (dictionaries containing data like messages).'''
            for event in graph.stream({'messages':("user",user_message)}):
                for value in event.values():
                    if 'messages' in value:
                        for msg in value["messages"]:
                            if hasattr(msg, 'content') and msg.content:
                                assistant_message = msg.content
                                with st.chat_message("assistant"):
                                    st.markdown(assistant_message)
                                st.session_state.chat_history.append({"role": "assistant", "content": assistant_message})

        elif usecase == "Chatbot with Tool":
            # Prepare state and invoke the graph
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state)
            
            for message in res['messages']:
                if type(message) == HumanMessage:
                    # Skip - already displayed
                    pass
                elif type(message) == ToolMessage:
                    tool_content = f"🔧 Tool Call:\n{message.content}"
                    with st.chat_message("assistant"):
                        st.info(tool_content)
                    st.session_state.chat_history.append({"role": "assistant", "content": tool_content})
                elif type(message) == AIMessage and message.content:
                    with st.chat_message("assistant"):
                        st.write(message.content)
                    st.session_state.chat_history.append({"role": "assistant", "content": message.content})
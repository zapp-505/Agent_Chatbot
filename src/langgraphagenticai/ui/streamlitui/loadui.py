import streamlit as st 

import os 

from src.langgraphagenticai.ui.uiconfigfile import Config

'''
We get the entire information about the functionalities the user wants from this frontend. Then we store that information and pass it towards the 
backend for enabling those routes and functionalites
'''
class LoadStreamlitUI:
    def __init__(self):
        self.config =Config()
        self.user_controls={}
    
    def load_streamlit_ui(self):
        st.set_page_config(page_title= "🤖 " + self.config.get_page_title(), layout="wide")
        st.header("🤖 " + self.config.get_page_title())


        with st.sidebar:
            llm_options=self.config.get_llm_options()
            usecase_options=self.config.get_usecase_options()

            self.user_controls["selected_llm"]=st.selectbox("Select LLM",llm_options)

            if self.user_controls["selected_llm"]=="Groq":
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_model"]=st.selectbox("Select Model",model_options)
                self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"]=st.text_input("API Key",type="password")

                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")

            self.user_controls["selected_usecase"]=st.selectbox("Select Usecases",usecase_options)

            if self.user_controls["selected_usecase"]=="Chatbot with Tool" or self.user_controls["selected_usecase"]=="AI news" :
                self.user_controls["TAVILY_API_KEY"] = st.session_state.get("TAVILY_API_KEY", "")
                self.user_controls["TAVILY_API_KEY"] = st.text_input("Tavily API Key", value=self.user_controls["TAVILY_API_KEY"], type="password")
                if not self.user_controls["TAVILY_API_KEY"]:
                     st.warning("⚠️ Please enter your Tavily API key to proceed.")

                if self.user_controls["selected_usecase"]=="AI news":
                    st.subheader("AI News Explorer")
                    news_options = self.config.get_news_options()
                    self.user_controls["news_option"]=st.selectbox("Select Time Frame",news_options)
                    st.session_state["news_option"] = self.user_controls["news_option"]

                if st.button("Fetch News", key="fetch_news_button"):
                    st.session_state["fetch_news_triggered"] = True
                    self.user_controls["fetch_news_triggered"] = True
        return self.user_controls
    
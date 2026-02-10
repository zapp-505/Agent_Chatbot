import os
import streamlit as st 
from langchain_groq import ChatGroq

class GroqLLM:
    def __init__(self,user_controls_input):
        self.user_controls_input = user_controls_input
    
    def get_llm_model(self):
        try:
            groq_api_key = self.user_controls_input.get("GROQ_API_KEY", "").strip()
            model_name = self.user_controls_input.get("selected_model")
            
            if not groq_api_key:
                st.error("Please enter the Groq API key")
                return None
            
            # Set environment variable
            os.environ["GROQ_API_KEY"] = groq_api_key
            
            llm = ChatGroq(api_key=groq_api_key, model=model_name)
        
        except Exception as e:
            raise ValueError(f"Error Occured with Exception: {e}")
        return llm
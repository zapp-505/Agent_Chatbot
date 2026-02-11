from src.langgraphagenticai.state.state import State

class NewsSummarizerNode:
    def __init__(self,model):
        self.llm=model
    
    def summarizer(self,news):
        prompt="Summarize and organize the news content in a proper markdown format with dates mentioned in order and valuable insights kept" 
           
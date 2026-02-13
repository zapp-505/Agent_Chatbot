from src.langgraphagenticai.state.state import State
from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import os

class NewsSummarizerNode:
    def __init__(self, model):
        """
        Initialize the NewsSummarizerNode with LLM and Tavily client.
        """
        self.llm = model
        self.tavily = None
        # Internal state to track workflow steps
        self.internal_state = {}
    
    def fetch_news(self, frequency: str):
        """
        Creates a node function that fetches AI news using Tavily API.
        
        Args:
            frequency (str): The time frame for news (daily, weekly, monthly, year)
        
        Returns:
            Callable node function that LangGraph can execute
        """
        def _fetch_node(state: State):
            self.internal_state['frequency'] = frequency
            
            # Initialize Tavily client with API key from environment
            if self.tavily is None:
                tavily_api_key = os.environ.get("TAVILY_API_KEY")
                if not tavily_api_key:
                    raise ValueError("TAVILY_API_KEY environment variable is not set. Please provide a valid Tavily API key.")
                self.tavily = TavilyClient(api_key=tavily_api_key)
            
            # Map frequency to Tavily API parameters
            time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
            days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}
            
            # Fetch news using Tavily client
            response = self.tavily.search(
                query="Top Artificial Intelligence (AI) technology news India and globally",
                topic="news",
                time_range=time_range_map.get(frequency, 'd'),
                include_answer="advanced",
                max_results=20,
                days=days_map.get(frequency, 1)
            )
            
            # Store news data in state
            news_data = response.get('results', [])
            self.internal_state['news_data'] = news_data
            
            # Return state with news data for next node
            return {
                "messages": state.get("messages", []),
                "news_data": news_data
            }
        
        return _fetch_node
    
    def summarizer(self, state: State):
        """
        Summarizes the fetched news using LLM with structured prompt.
        
        Args:
            state (State): The state dictionary containing 'news_data'
        
        Returns:
            Dictionary with summarized news message
        """
        news_items = self.internal_state.get('news_data', [])
        
        if not news_items:
            response = self.llm.invoke("No news data available to summarize.")
            return {"messages": state.get("messages", []) + [response]}
        
        # Create structured prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Summarize AI news articles into markdown format. For each item include:
            - Date in **YYYY-MM-DD** format in IST timezone
            - Concise summary from latest news (2-3 sentences)
            - Sort news by date (latest first)
            - Source URL as clickable link
            
            Use format:
            ### [Date]
            - **[Title/Topic]**: [Summary] [Read more](URL)
            
            Provide insights and trends at the end."""),
            ("user", "Articles:\n{articles}")
        ])
        
        # Format articles for the prompt
        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}\nTitle: {item.get('title', '')}"
            for item in news_items
        ])
        
        # Generate summary using chain
        chain = prompt_template | self.llm
        response = chain.invoke({"articles": articles_str})
        summary = response.content
        self.internal_state['summary'] = summary
        
        # Optionally save to file
        self._save_result()
        
        return {"messages": state.get("messages", []) + [response]}
    
    def _save_result(self):
        """
        Save the news summary to a markdown file.
        Internal method called after summarization.
        """
        try:
            frequency = self.internal_state.get('frequency', 'unknown')
            summary = self.internal_state.get('summary', '')
            
            # Create directory if it doesn't exist
            os.makedirs("./AINews", exist_ok=True)
            
            filename = f"./AINews/{frequency}_summary.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
                f.write(summary)
            
            self.internal_state['filename'] = filename
            print(f"✓ News summary saved to {filename}")
        except Exception as e:
            print(f"Warning: Could not save file - {e}")
import asyncio
import pandas as pd
from backend.agents.data_agent import create_graph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

async def test_search():
    print("Creating dummy dataframe...")
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    
    print("Initializing graph...")
    app = create_graph(df)
    
    question = "What is the current latest stable version of Python?"
    print(f"Asking: {question}")
    
    messages = [HumanMessage(content=question)]
    
    async for event in app.astream_events({"messages": messages}, version="v1"):
        kind = event["event"]
        if kind == "on_tool_start":
            print(f"Tool Started: {event['name']}")
        elif kind == "on_tool_end":
            print(f"Tool Output: {str(event['data'].get('output'))[:100]}...") # Truncate output
        elif kind == "on_chat_model_stream":
            pass # Ignore tokens for cleaner output

    print("Test finished.")

if __name__ == "__main__":
    asyncio.run(test_search())

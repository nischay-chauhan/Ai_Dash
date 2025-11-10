from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

def call_groq_insights(prompt: str, model: str = "openai/gpt-oss-20b") -> str:
    """
    Generate insights using Groq's API with the OpenAI client.
    
    Args:
        prompt: The prompt to send to the model
        model: The model to use (defaults to gpt-oss-20b)
        
    Returns:
        str: The generated response text
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a data insights assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error calling Groq API: {str(e)}")

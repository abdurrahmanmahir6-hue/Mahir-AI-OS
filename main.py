import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    print("Welcome to Mahir-AI-OS!")
    
    # Accessing API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if openai_key and openai_key != "your_actual_openai_key_here":
        print("✅ OpenAI API Key loaded successfully.")
    else:
        print("⚠️ OpenAI API Key not found or still using placeholder.")

    if gemini_key and gemini_key != "your_actual_gemini_key_here":
        print("✅ Gemini API Key loaded successfully.")
    else:
        print("⚠️ Gemini API Key not found or still using placeholder.")

    if tavily_key and tavily_key != "your_actual_tavily_key_here":
        print("✅ Tavily API Key loaded successfully.")
    else:
        print("⚠️ Tavily API Key not found or still using placeholder.")

if __name__ == "__main__":
    main()

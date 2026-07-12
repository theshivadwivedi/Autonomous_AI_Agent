# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()

# def get_llm() -> ChatGoogleGenerativeAI:

#     api_key = os.getenv("GOOGLE_API_KEY")

#     if not api_key:
#         raise ValueError("GOOGLE_API_KEY is not found in .env")
    
#     return ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         temperature= 0.2, 
#         google_api_key= api_key,
#     )
      

from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

load_dotenv()

def get_llm():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not found in .env")
    
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )



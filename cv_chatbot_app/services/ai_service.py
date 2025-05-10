import os
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def get_groq_client():
    """Returns a configured Groq client"""
    return groq.Client(api_key=GROQ_API_KEY)

def generate_response(context, question):
    client = get_groq_client()
    
    system_prompt = (
        "You are an intelligent AI assistant that reviews a candidate's CV and answers questions about their experience. "
        "Use only the provided CV text. Generate a natural, concise answer based on what's present. "
        "If the CV mentions something, summarize it clearly and refer to specific projects or sections if applicable. "
        "If something is not in the CV, state that it’s not mentioned, but do not guess or invent information. "
        "Keep your response brief, factual, and helpful—no fluff or unnecessary politeness."
        "dont be like, your CV, its not mine and not yours, its just a CV, so be like, "
    )

    user_prompt = f"CV:\n{context}\n\nQ: {question}\nA:"
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Error"

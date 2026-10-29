from groq import Groq
import os
from dotenv import load_dotenv
from ai_stack.config import LLM_MODEL

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
cliente = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_completion(messages):
    chat = cliente.chat.completions.create(model=LLM_MODEL, messages=messages,response_format={"type": "json_object"})
    return chat.choices[0].message.content

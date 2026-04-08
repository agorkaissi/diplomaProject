from langchain_ollama import ChatOllama

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.2:1b"

llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
    timeout=60
)

def generate_answer(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content
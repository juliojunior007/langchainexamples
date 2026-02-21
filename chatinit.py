
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def somar(a: int, b: int) -> int:
    """soma dois números"""
    return a + b

@tool
def clima(cidade: str) -> str:
    """Consulta o clima de uma cidade"""
    return f"O clima em {cidade} está 28ºC, ensolarado." 


# Modelo com configuração customizadas
llm = init_chat_model(
    "gpt-4o-mini",
    temperature=0.2,
    max_tokens=150,
)

# Passa o modelo configurado pro agente
agent = create_agent(
    model=llm,
    tools=[somar, clima],
    system_prompt="Você é um assistente útil que responde em português"
)

print("Chat com agente + temperatura (digite 'sair' pra encerrar)\n")

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break
    resposta = llm.invoke(pergunta)
    print(f"ChatGPT 🤖: {resposta.content}\n")
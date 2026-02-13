import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# 1. Carrega as chaves do .env
load_dotenv()

# 2. Inicializa o modelo da OpenAI
# O LangChain vai ler a OPENAI_API_KEY automaticamente do ambiente
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. Define uma ferramenta de teste (Tool)
def get_weather(city: str):
    """Consulta o clima de uma cidade."""
    if "bauru" in city.lower():
        return "Fazendo um sol de rachar, tipico do interior!"
    return "Tempo nublado com chance de chuva."

tools = [get_weather]

# 4. Cria o agente usando LangGraph
agent_executor = create_react_agent(model, tools)

# 5. Executa e envia para o LangSmith
def run_test():
    query = {"messages": [("user", "Como está o tempo em Bauru?")]}
    print("--- Iniciando Agente ---")
    for event in agent_executor.stream(query):
        print(event)
    print("--- Finalizado! Verifique o painel do LangSmith ---")

if __name__ == "__main__":
    run_test()
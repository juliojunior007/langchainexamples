# main.py
import os
from dotenv import load_dotenv
from model_factory import get_model

# 1. LIGA O MONITORAMENTO (O interruptor geral)
# O LangChain lê as chaves do .env e ativa o rastreio automaticamente
load_dotenv()

def orquestrador():
    print("\n--- 🦅 ORQUESTRADOR GUARDIÃO FÊNIX ATIVADO ---")
    print("--- 📡 Monitoramento LangSmith: ON ---")

    # 2. SOLICITA O MODELO (Usando sua Factory)
    # Escolhemos o gpt-4o-mini por ser 90% mais barato que o Opus para testes
    llm = get_model(model_name="gpt-4o-mini", temperature=0.7)
    
    print(f"🤖 Motor em uso: {llm.model_name}\n")

    while True:
        pergunta = input("Você: ")
        
        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("\nEncerrando Orquestrador... Até logo, Julio!")
            break

        print("\n--- 🧠 Pensando... (Verifique o LangSmith) ---")
        
        # 3. EXECUÇÃO
        # Como o Tracing está ativo, essa chamada gera um log completo
        resposta = llm.invoke(pergunta)
        
        print(f"\nGuardião: {resposta.content}\n")
        print("-" * 40)

if __name__ == "__main__":
    orquestrador()
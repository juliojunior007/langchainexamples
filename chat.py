# chat1.py
from model_factory import get_model

# Usa gpt-4o-mini por padrão (rápido e barato para estudos)
llm = get_model()

print("--- Chat Iniciado (digite 'sair' para encerrar) ---\n")

while True:
    pergunta = input("🚀: ")
    if pergunta.lower() == "sair":
        break
    
    resposta = llm.invoke(pergunta)
    print(f"🤖: {resposta.content}\n")
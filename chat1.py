from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


llm = ChatOpenAI(model="gpt-4o-mini")

print("Chat com GPT (digite 'sair' pra encerrar)\n")

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break
    resposta = llm.invoke(pergunta)
    print(f"🤖: {resposta.content}\n")

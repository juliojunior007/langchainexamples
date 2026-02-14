from dotenv import load_dotenv
load_dotenv()
from model_factory import get_model # imports das credenciais do model_factory
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

# Tools simples
@tool
def somar(a: int, b: int) -> int:
    """Soma dois números"""
    return a + b

@tool
def multiplicar(a: int, b: int) -> int:
    """Multiplica dois números"""
    return a * b

@tool
def clima(cidade: str) -> str:
    """Consulta o clima de uma cidade"""
    return f"O clima em {cidade} está 28°C, ensolarado."

# Checkpointer em memória
checkpointer = InMemorySaver()

# Cria o agente com memória
llm = get_model(model_name="gpt-4o-mini")
agent = create_agent(
    model="gpt-4o-mini",
    tools=[somar, multiplicar, clima],
    system_prompt="Você é um assistente útil que responde em português.",
    checkpointer=checkpointer
)

print("Chat com Memória (digite 'sair' pra encerrar)\n")

config = {"configurable": {"thread_id": "conversa-1"}}

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break

    # Ver o que tá na memória ANTES de responder
    estado = agent.get_state(config)
    print(f"\n  📝 Mensagens na memória: {len(estado.values.get('messages', []))}")
    for m in estado.values.get("messages", []):
        print(f"     [{m.__class__.__name__}] {m.content[:80] if m.content else '[tool call]'}")
    print()

    resultado = agent.invoke(
        {"messages": [{"role": "user", "content": pergunta}]},
        config=config
    )

    for msg in resultado["messages"]:
        tipo = msg.__class__.__name__
        if tipo == "AIMessage" and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  🔧 Tool chamada: {tc['name']}({tc['args']})")
        elif tipo == "ToolMessage":
            print(f"  📦 Resultado: {msg.content}")
        elif tipo == "AIMessage" and msg.content:
            print(f"ChatGPT: {msg.content}\n")
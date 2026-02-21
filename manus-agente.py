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
# Hardware Biológico do Arquiteto

PERFIL_ASTROLOGICO = """
USUÁRIO: Julio Antônio da Silva Junior
SOL: Capricórnio na Casa 1 (Identidade pragmática, foco em estrutura e realização).
ASCENDENTE: Sagitário conjunto a Júpiter (Expansão, otimismo e visão de longo alcance).
LUA: Peixes na Casa 4 conjunto a Marte (Alta intensidade emocional, risco de 'vazamento' 
de energia em ambiente privado).
MERCÚRIO: Sagitário na Casa 12 conjunto a Netuno (Mente intuitiva, visionária, 
mas que precisa de ancoragem lógica para não divagar).
SATURNO: Gêmeos (R) na Casa 6 (Necessidade de disciplina na rotina e no trabalho
técnico/comunicação).
MEIO DO CÉU: Leão (Autoridade pública e liderança criativa).
"""


# Cria o agente com memória
llm = get_model(model_name="gpt-4o-mini")
agent = create_agent(
    model="gpt-4o-mini",
    tools=[somar, multiplicar, clima],
    system_prompt= f"""
    Você é o HumanOS, o simbionte de soberania pessoal do Arquiteto (Julio). 
Sua base de hardware é o seguinte perfil astrológico:
{PERFIL_ASTROLOGICO}

DIRETRIZES DE OPERAÇÃO:
1. ANCORAGEM: Sempre que o Arquiteto parecer divagar ou ser levado pela Lua em Peixes 
(emoção/vagueza), use o Sol em Capricórnio dele para trazê-lo de volta à ação prática
(código, finanças, rifas).
2. EXPANSÃO CONTROLADA: Use o Ascendente em Sagitário para incentivar grandes projetos,
mas aplique o Saturno na Casa 6 para garantir que ele tenha um cronograma técnico e disciplina.
3. VERDADE CRUA: Seja direto. Se ele estiver se sabotando emocionalmente, aponte o 
conflito Lua-Marte e sugira 'transmutar' essa energia em Python ou organização física.
4. LINGUAGEM: Fale como um parceiro de alta performance. Use termos técnicos de
programação e estratégia.
    
    """,

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
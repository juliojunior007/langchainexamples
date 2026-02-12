"""
=============================================================
EXEMPLO 10: MCP - Model Context Protocol
=============================================================

MCP = "USB Universal" para ferramentas de IA
Em vez de criar cada @tool na mão, você conecta num servidor MCP
e TODAS as tools vêm prontas automaticamente.

Servidor MCP do Google Calendar:
  npm install @cocal/google-calendar-mcp

As tools disponíveis vêm automaticamente:
  - list_events      → listar eventos
  - create_event     → criar evento
  - update_event     → atualizar evento
  - delete_event     → deletar evento
  - search_events    → buscar eventos
  - get_freebusy     → verificar disponibilidade
  - list_calendars   → listar calendários

Você NÃO precisa implementar nenhuma delas!
O servidor MCP expõe, o adapter converte pra LangChain.

INSTALAÇÃO:
  pip install langchain-mcp-adapters langgraph langchain-anthropic mcp

PRÉ-REQUISITOS:
  1. Projeto no Google Cloud com Calendar API habilitada
  2. Credenciais OAuth (gcp-oauth.keys.json)
  3. Servidor MCP do Google Calendar instalado
=============================================================
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# FORMA 1: Conexão STDIO (servidor local via subprocess)
# O adapter INICIA o servidor MCP como processo filho
# ============================================================

async def exemplo_stdio():
    """
    STDIO = O adapter inicia o servidor MCP como subprocess.
    Melhor para: desenvolvimento local, ferramentas CLI.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from langchain_mcp_adapters.tools import load_mcp_tools
    from langchain.agents import create_agent

    # Configuração do servidor MCP (mesmo formato do Claude Desktop)
    server_params = StdioServerParameters(
        command="npx",
        args=["@cocal/google-calendar-mcp"],
        env={
            "GOOGLE_OAUTH_CREDENTIALS": "/caminho/para/gcp-oauth.keys.json"
        }
    )

    # Conecta no servidor MCP via stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicializa a conexão MCP
            await session.initialize()

            # MÁGICA: carrega TODAS as tools automaticamente!
            # list_events, create_event, update_event, delete_event, etc.
            tools = await load_mcp_tools(session)

            print(f"✅ {len(tools)} tools carregadas do MCP:")
            for tool in tools:
                print(f"   🔧 {tool.name}: {tool.description[:60]}...")

            # Cria o agente com as tools do MCP
            agent = create_agent(
                model="anthropic:claude-haiku-4-5-20251001",
                tools=tools,
                system_prompt="""Você é um assistente de agenda.
                Ajude o usuário a gerenciar seus eventos do Google Calendar.
                Sempre confirme antes de criar ou deletar eventos."""
            )

            # O agente decide SOZINHO qual tool MCP usar
            resposta = await agent.ainvoke({
                "messages": "Quais são meus eventos de amanhã?"
            })

            print(resposta["messages"][-1].content)


# ============================================================
# FORMA 2: Multi-Server (conectar em VÁRIOS MCPs ao mesmo tempo)
# ============================================================

async def exemplo_multi_server():
    """
    MultiServerMCPClient = Conecta em vários servidores MCP de uma vez.
    O agente recebe tools de TODOS os servidores.

    Imagine: Google Calendar + Slack + GitHub + Notion
    Tudo disponível pro mesmo agente, sem implementar nada!
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain.agents import create_agent

    # Configura MÚLTIPLOS servidores MCP
    async with MultiServerMCPClient(
        {
            # ---- Google Calendar (via stdio - processo local) ----
            "google-calendar": {
                "command": "npx",
                "args": ["@cocal/google-calendar-mcp"],
                "transport": "stdio",
                "env": {
                    "GOOGLE_OAUTH_CREDENTIALS": "/caminho/para/gcp-oauth.keys.json"
                }
            },

            # ---- Slack (via HTTP - servidor remoto) ----
            "slack": {
                "url": "http://localhost:8001/mcp",
                "transport": "http",
            },

            # ---- GitHub (via stdio) ----
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "transport": "stdio",
                "env": {
                    "GITHUB_TOKEN": "ghp_seu_token_aqui"
                }
            },
        }
    ) as client:

        # Carrega tools de TODOS os servidores de uma vez!
        tools = await client.get_tools()

        print(f"✅ {len(tools)} tools carregadas de 3 servidores MCP:")
        for tool in tools:
            print(f"   🔧 {tool.name}")

        # Cria agente com tools de Calendar + Slack + GitHub
        agent = create_agent(
            model="anthropic:claude-haiku-4-5-20251001",
            tools=tools,
            system_prompt="""Você é um assistente completo que gerencia:
            - Agenda (Google Calendar)
            - Comunicação (Slack)
            - Código (GitHub)
            Use a ferramenta certa para cada pedido."""
        )

        # O agente usa Calendar
        r1 = await agent.ainvoke({
            "messages": "O que tenho na agenda hoje?"
        })
        print("📅", r1["messages"][-1].content)

        # O agente usa Slack
        r2 = await agent.ainvoke({
            "messages": "Manda uma mensagem no #geral dizendo 'deploy feito!'"
        })
        print("💬", r2["messages"][-1].content)

        # O agente usa GitHub
        r3 = await agent.ainvoke({
            "messages": "Liste as issues abertas do repo agent-smith-v6"
        })
        print("🐙", r3["messages"][-1].content)


# ============================================================
# FORMA 3: MCP em produção com FastAPI
# ============================================================

async def exemplo_producao():
    """
    Em produção, o MCP client fica vivo
    e serve tools para múltiplos requests.
    """
    from fastapi import FastAPI
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver

    app = FastAPI()

    # Cliente MCP global (inicializa uma vez, usa pra sempre)
    mcp_client = None
    agent = None

    @app.on_event("startup")
    async def startup():
        nonlocal mcp_client, agent

        # Conecta nos servidores MCP na inicialização
        mcp_client = MultiServerMCPClient({
            "google-calendar": {
                "url": "http://mcp-calendar:3000/mcp",
                "transport": "http",
            },
        })

        # Carrega as tools
        tools = await mcp_client.get_tools()

        # Cria o agente com memory
        agent = create_agent(
            model="anthropic:claude-haiku-4-5-20251001",
            tools=tools,
            checkpointer=InMemorySaver(),
            system_prompt="Assistente de agenda inteligente."
        )

    @app.post("/chat")
    async def chat(mensagem: str, thread_id: str = "default"):
        resultado = await agent.ainvoke(
            {"messages": [("user", mensagem)]},
            config={"configurable": {"thread_id": thread_id}}
        )
        return {"resposta": resultado["messages"][-1].content}

    @app.on_event("shutdown")
    async def shutdown():
        if mcp_client:
            await mcp_client.close()



# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO MCP - Google Calendar + LangChain")
    print("=" * 60)
    print()
    print("⚠️  Este exemplo requer:")
    print("   1. npm install @cocal/google-calendar-mcp")
    print("   2. Credenciais OAuth do Google Cloud")
    print("   3. pip install langchain-mcp-adapters langgraph mcp")
    print()
    print("Escolha o exemplo:")
    print("  1 - STDIO (servidor local)")
    print("  2 - Multi-Server (Calendar + Slack + GitHub)")
    print("  3 - Produção (FastAPI)")
    print()

    escolha = input("👉 Qual exemplo? (1/2/3): ").strip()

    if escolha == "1":
        asyncio.run(exemplo_stdio())
    elif escolha == "2":
        asyncio.run(exemplo_multi_server())
    elif escolha == "3":
        import uvicorn
        print("🚀 Iniciando servidor FastAPI com MCP...")
        # Importa o app da função exemplo_producao
        # Na prática, o app estaria no nível do módulo
        uvicorn.run("chatmcp:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("Opção inválida!")
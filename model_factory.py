# model_factory.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Garante que o .env foi carregado
load_dotenv()

def get_model(model_name=None, temperature=0, max_tokens=None):
    """
    Retorna uma instância de ChatOpenAI configurada.
    
    Args:
        model_name: Qual modelo usar (ex: "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo")
        temperature: Controla criatividade (0=determinístico, 1=criativo)
        max_tokens: Limite de tokens na resposta (None = sem limite)
    
    Returns:
        ChatOpenAI: Instância pronta para usar
    """
    
    # Padrão: gpt-4o-mini (rápido, barato, bom para estudos)
    if not model_name:
        model_name = "gpt-4o-mini"
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("⚠️ OPENAI_API_KEY não encontrada no .env")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key
    )
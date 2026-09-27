"""
Configurações do Assistente Virtual Financeiro Aurélios.
"""

from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Arquivos da Base de Conhecimento
PATH_PERFIL = DATA_DIR / "perfil_investidor.json"
PATH_PRODUTOS = DATA_DIR / "produtos_financeiros.json"
PATH_TRANSACOES = DATA_DIR / "transacoes.csv"
PATH_HISTORICO = DATA_DIR / "historico_atendimento.csv"

# Configuração de Provedores de LLM
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "llama3"

DEFAULT_OPENAI_COMPATIBLE_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

# Configurações do Agente Aurélios
AGENT_NAME = "Aurélios"
AGENT_ROLE = "Mentor e Assistente Virtual Financeiro Inteligente"
REQUEST_TIMEOUT = 30  # segundos

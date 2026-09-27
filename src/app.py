"""
Aurélios — Assistente Virtual Financeiro (Dicas de Investimento e Economia).
Execução direta via terminal/CLI, utilizando Pandas, JSON e Requests.
"""

import sys
import os
from typing import Optional

# Configura encoding UTF-8 no console Windows se disponível
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from agente import AureliosAgent
from config import (
    DEFAULT_OLLAMA_URL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OPENAI_COMPATIBLE_URL,
    DEFAULT_OPENAI_MODEL,
    AGENT_NAME,
)


def formatar_real(val: float) -> str:
    """Formata valores monetários no padrão brasileiro (R$ 1.000,00)."""
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class AureliosCLI:
    """Interface de Linha de Comando interativa para o Aurélios."""

    def __init__(self):
        self.agente = AureliosAgent()
        self.provedor = "standalone"  # Padrão: standalone, ollama ou openai
        self.url_api = DEFAULT_OLLAMA_URL
        self.modelo = DEFAULT_OLLAMA_MODEL
        self.api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)

    def cabecalho(self) -> None:
        """Exibe o cabeçalho institucional do assistente."""
        print("=" * 72)
        print(f"      {AGENT_NAME.upper()} - ASSISTENTE DE INVESTIMENTO E ECONOMIA")
        print("   Inteligência Financeira com Base em Dados Concretos (Pandas e JSON)")
        print("=" * 72)

    def _nome_provedor_amigavel(self) -> str:
        if self.provedor == "ollama":
            return f"Ollama Local ({self.modelo})"
        elif self.provedor in ["openai", "groq"]:
            return f"API Nuvem ({self.modelo})"
        return "Motor Autônomo Local (Regras e Pandas)"

    def demonstrativo_gastos(self) -> None:
        """Exibe a distribuição detalhada de despesas por categoria via Pandas."""
        analise = self.agente.calcular_analise_gastos()
        print("\n" + "=" * 72)
        print("DEMONSTRATIVO DETALHADO DE GASTOS POR CATEGORIA (PANDAS)")
        print("=" * 72)

        if not analise["gastos_por_categoria"]:
            print("Nenhuma despesa registrada.")
            return

        linhas = []
        for cat, val in analise["gastos_por_categoria"].items():
            pct = (val / analise["total_despesas"] * 100) if analise["total_despesas"] > 0 else 0
            linhas.append({
                "Categoria": cat.capitalize(),
                "Valor": formatar_real(val),
                "Participação": f"{pct:.1f}%"
            })

        df_tabela = pd.DataFrame(linhas)
        print(df_tabela.to_string(index=False))
        print("-" * 72)
        print(f"Total Geral de Saídas: {formatar_real(analise['total_despesas'])}")
        print(f"Maior Categoria:       {analise['maior_categoria'][0].capitalize()} ({formatar_real(analise['maior_categoria'][1])})")
        print(f"Saldo Mensal Livre:    {formatar_real(analise['saldo_mensal'])}")
        print("=" * 72)

    def demonstrativo_produtos(self) -> None:
        """Exibe os produtos homologados e recomendações de adequação."""
        print("\n" + "=" * 72)
        print("CATÁLOGO DE PRODUTOS FINANCEIROS HOMOLOGADOS")
        print("=" * 72)
        for i, prod in enumerate(self.agente.produtos, start=1):
            print(f"[{i}] {prod['nome']} ({prod['categoria'].upper()})")
            print(f"    Risco:             {prod['risco'].capitalize()}")
            print(f"    Rentabilidade:     {prod['rentabilidade']}")
            print(f"    Aplicação Mínima:  {formatar_real(prod['aporte_minimo'])}")
            print(f"    Público Indicado:  {prod['indicado_para']}")
            print()
        print("=" * 72)

    def configurar_provedor(self) -> None:
        """Permite alternar o provedor de inferência diretamente no console."""
        print("\n" + "=" * 72)
        print("CONFIGURAÇÃO DO PROVEDOR DE IA")
        print("=" * 72)
        print(f"Provedor Ativo: {self._nome_provedor_amigavel()}\n")
        print("[1] Modo Autônomo Local (Padrão: análise via Pandas e regras - sem dependência externa)")
        print("[2] Ollama Local (Requer servidor Ollama rodando em http://localhost:11434)")
        print("[3] API OpenAI / Groq / Compatível (Requer endpoint e Chave de API)")
        print("[0] Cancelar e manter configuração atual")
        print("-" * 72)

        escolha = input("Selecione a opção desejada: ").strip()

        if escolha == "1":
            self.provedor = "standalone"
            print("\n[OK] Configurado para Modo Autônomo Local.")
        elif escolha == "2":
            self.provedor = "ollama"
            url = input(f"URL do Ollama [{self.url_api}]: ").strip()
            if url:
                self.url_api = url
            modelo = input(f"Nome do Modelo [{self.modelo}]: ").strip()
            if modelo:
                self.modelo = modelo
            print(f"\n[OK] Configurado para Ollama Local ({self.modelo} em {self.url_api}).")
        elif escolha == "3":
            self.provedor = "openai"
            url = input(f"Endpoint da API [{DEFAULT_OPENAI_COMPATIBLE_URL}]: ").strip()
            self.url_api = url or DEFAULT_OPENAI_COMPATIBLE_URL
            modelo = input(f"Modelo [{DEFAULT_OPENAI_MODEL}]: ").strip()
            self.modelo = modelo or DEFAULT_OPENAI_MODEL
            key = input("Chave de API (Bearer Token): ").strip()
            if key:
                self.api_key = key
            print(f"\n[OK] Configurado para API Externa ({self.modelo}).")
        else:
            print("\nConfiguração mantida.")

    def processar_pergunta(self, pergunta: str) -> None:
        """Processa perguntas e exibe a resposta formatada do Aurélios."""
        print("\nAurélios está analisando...")
        resposta, origem = self.agente.responder_com_llm(
            mensagem_usuario=pergunta,
            provedor=self.provedor,
            url_api=self.url_api,
            modelo=self.modelo,
            api_key=self.api_key,
        )
        print(f"\nAurélios [Fonte: {origem}]:")
        print("-" * 72)
        print(resposta)
        print("-" * 72)

    def executar(self) -> None:
        """Loop principal da aplicação de terminal."""
        self.cabecalho()

        while True:
            print("\nMENU PRINCIPAL:")
            print("[1] Dicas Práticas de Economia e Redução de Gastos")
            print("[2] Dicas de Investimento e Alocação Estratégica")
            print("[3] Demonstrativo Detalhado de Gastos (Pandas)")
            print("[4] Diagnóstico da Reserva de Emergência e Metas")
            print("[5] Catálogo de Produtos Homologados")
            print("[6] Configurar Provedor de IA (Autônomo / Ollama / Nuvem)")
            print("[7] Recarregar Dados da Pasta data/")
            print("[0] Encerrar Aplicação")
            print("-" * 72)
            print("Digite o número da opção OU escreva sua pergunta diretamente:")
            print("-" * 72)

            entrada = input("Você: ").strip()
            if not entrada:
                continue

            if entrada in ["0", "sair", "exit", "quit"]:
                print(f"\nEncerrando sessão com {AGENT_NAME}. Gestão financeira prudente e até logo.")
                break

            elif entrada == "1":
                self.processar_pergunta("Quais as melhores dicas de economia e corte de gastos para meu orçamento?")
            elif entrada == "2":
                self.processar_pergunta("Quais as melhores dicas de investimento recomendadas para meu perfil?")
            elif entrada == "3":
                self.demonstrativo_gastos()
            elif entrada == "4":
                self.processar_pergunta("Como está minha reserva de emergência e quanto falta para a meta?")
            elif entrada == "5":
                self.demonstrativo_produtos()
            elif entrada == "6":
                self.configurar_provedor()
            elif entrada == "7":
                self.agente.carregar_dados()
                print("\n[OK] Dados recarregados com sucesso a partir dos arquivos CSV e JSON.")
            else:
                self.processar_pergunta(entrada)


if __name__ == "__main__":
    cli = AureliosCLI()
    cli.executar()

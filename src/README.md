# Código da Aplicação — Aurélios (Interface CLI de Terminal)

Esta pasta contém o código-fonte do **Aurélios**, Assistente Virtual Financeiro Inteligente projetado para execução direta e ágil no terminal, eliminando dependências pesadas de interface web e garantindo máxima velocidade e manutenção limpa.

## Estrutura dos Arquivos

```
src/
├── app.py              # Interface interativa de linha de comando (CLI)
├── agente.py           # Classe AureliosAgent com regras de negócio, Pandas, JSON e Requests
├── config.py           # Definições de caminhos, endpoints de LLM e constantes
├── requirements.txt    # Dependências mínimas essenciais (pandas, requests)
└── test_agente.py      # Testes automatizados de validação analítica e comportamental
```

## Tecnologias Utilizadas

- **Pandas**: Manipulação de dados, agrupamento de despesas por categoria, cálculo de totais, balanço mensal e métricas de reserva.
- **JSON**: Leitura e serialização do perfil do investidor e catálogo de produtos financeiros homologados.
- **Requests**: Comunicação via HTTP REST com APIs de LLMs (Ollama local, OpenAI, Groq Cloud, OpenRouter).
- **Python Nativo (CLI)**: Menu interativo estruturado, formatador monetário em padrão brasileiro e modo de conversação contínua.

## Como Executar a Aplicação

### 1. Instalar as Dependências

```bash
pip install -r src/requirements.txt
```

### 2. Iniciar o Aurélios no Terminal

```bash
python src/app.py
```

---

## Funcionalidades do Menu Interativo

A aplicação inicia de forma limpa e direta, com um menu altamente funcional onde o usuário pode escolher as opções numeradas ou digitar qualquer dúvida financeira diretamente no prompt:

1. **[1] Dicas Práticas de Economia e Redução de Gastos:** Orientações sobre a regra 50/30/20, corte de gastos na maior despesa (moradia/alimentação) e eliminação de gastos fantasmas.
2. **[2] Dicas de Investimento e Alocação Estratégica:** Orientações de aportes para completar a reserva de emergência, produtos com isenção de IR (LCI/LCA) e poder dos juros compostos.
3. **[3] Demonstrativo Detalhado de Gastos (Pandas):** Exibe tabela com a distribuição de despesas por categoria calculadas pelo Pandas.
4. **[4] Diagnóstico da Reserva de Emergência e Metas:** Mostra o saldo acumulado (R$ 10.000,00), o déficit para a meta de R$ 15.000,00 e o plano de aportes.
5. **[5] Catálogo de Produtos Homologados:** Lista produtos de Renda Fixa e Fundos com rentabilidade, risco e aplicação mínima.
6. **[6] Configurar Provedor de IA:** Permite alternar entre Motor Autônomo Local, Ollama Local ou APIs Externas (OpenAI/Groq).
7. **[7] Recarregar Dados da Pasta data/:** Revalida e recarrega em tempo real os arquivos CSV e JSON.
8. **[0] Encerrar Aplicação.**

> **Prompt Aberto:** Você pode digitar perguntas diretamente a qualquer momento no prompt (ex: *"Como economizar no supermercado?"*, *"O que é Taxa Selic?"*, *"Vale a pena CDB ou LCI?"*). Aurélios analisa e responde de imediato.

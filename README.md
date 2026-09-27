# Aurélios — Assistente Virtual Financeiro: Dicas de Investimento e Economia com IA

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![CLI](https://img.shields.io/badge/Interface-Terminal%20CLI-0d47a1.svg)](https://docs.python.org/3/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)](https://pandas.pydata.org/)
[![Requests](https://img.shields.io/badge/Requests-HTTP%20API-orange.svg)](https://requests.readthedocs.io/)
[![DIO](https://img.shields.io/badge/DIO-Lab%20BIA%20do%20Futuro-red.svg)](https://www.dio.me/)

> **Aurélios** é um mentor e assistente virtual financeiro inteligente desenvolvido para o desafio de projeto da **Digital Innovation One (DIO)**: *"Construa Seu Assistente Virtual Com Inteligência Artificial"*, inspirado na revolução dos assistentes virtuais de inteligência artificial no setor financeiro.

Inspirado na disciplina, racionalidade e sabedoria prática do imperador filósofo Marco Aurélio, o **Aurélios** é especializado em fornecer **dicas pragmáticas de investimento** e **estratégias inteligentes de economia doméstica**, atuando através de uma **interface de terminal (CLI)** ágil, limpa e corporativa, ancorada em dados concretos com **Pandas** e **JSON**, livre de alucinações.

---

## Destaques da Solução

- **Especialista em Investimento e Economia:** Fornece recomendações orientadas a resultados para redução de despesas (método 50/30/20, corte de supérfluos, renegociação de contas) e estratégias de investimento em Renda Fixa (Tesouro Selic, CDB, LCI, LCA, IPCA+) e diversificação prudente;
- **Interface de Terminal (CLI) Rápida e Limpa:** Execução direta no console sem a lentidão ou erros de renderização típicos de frameworks web pesados;
- **Menu Funcional com Prompt Unificado:** O menu principal aceita tanto números de opções rápidas quanto **qualquer pergunta em linguagem natural digitada diretamente no console**, sem obrigar o usuário a transitar por submenus;
- **Motor Contábil com Pandas:** Análise rigorosa e determinística de transações e extratos (`transacoes.csv`), eliminando erros de cálculo e alucinações matemáticas comuns em LLMs;
- **Grounding em Dados Reais:** Base de dados em `JSON` e `CSV` contendo perfil de investidor (`perfil_investidor.json`), metas orçamentárias e catálogo de produtos homologados (`produtos_financeiros.json`);
- **Parâmetros Aumentados de IA Generativa:** Configuração refinada de inferência (`temperatura: 0.7`, `max_tokens/num_predict: 1200`, `top_p: 0.9`) via biblioteca **Requests**, viabilizando respostas profundas, analíticas e didáticas;
- **Flexibilidade de Provedores:** Suporte nativo ao **Motor Autônomo Local** (sem dependência externa), **Ollama Local** (100% privado) e **APIs em Nuvem** (OpenAI, Groq e compatíveis);
- **Segurança da Informação e LGPD:** Proteção contra vazamento de credenciais, blindagem de senhas bancárias e respeito estrito ao perfil de risco (*suitability*).

---

## Arquitetura da Solução

```mermaid
flowchart TD
    subgraph Frontend["Interface do Usuário (Terminal / CLI)"]
        UI["Console Interativo (Menu Funcional & Prompt Unificado)"]
        Demonstrativo["Demonstrativo Tabular de Despesas (Pandas)"]
    end

    subgraph Backend["Aplicação Python (src/agente.py & src/app.py)"]
        Agente[Orquestrador Aurélios]
        DataEngine["Engine de Dados (Pandas + JSON)"]
        PromptBuilder[Montador de Contexto & Grounding]
        Guardrails[Camada de Segurança & Anti-Alucinação]
        FallbackEngine[Motor Autônomo Local / Heurístico]
    end

    subgraph Data["Base de Conhecimento (data/)"]
        D1[(transacoes.csv)]
        D2[(perfil_investidor.json)]
        D3[(produtos_financeiros.json)]
        D4[(historico_atendimento.csv)]
    end

    subgraph LLM["Camada de IA Generativa (via Requests)"]
        Ollama[Ollama Local: Llama 3 / Mistral]
        CloudAPI[API OpenAI / Groq Cloud]
    end

    UI -->|Opção [1-7] ou Pergunta Direta| Agente
    Demonstrativo -->|Renderiza Tabela Formatada| UI
    DataEngine -->|Lê e Processa com Pandas/JSON| D1 & D2 & D3 & D4
    Agente --> DataEngine
    DataEngine --> PromptBuilder
    PromptBuilder --> Guardrails
    Guardrails -->|Requisição HTTP REST| LLM
    Guardrails -.->|Caso Offline / Standalone| FallbackEngine
    LLM -->|Resposta JSON (temp=0.7, tokens=1200)| Agente
    FallbackEngine -->|Resposta Estruturada| Agente
    Agente -->|Texto Formatado + Origem| UI
```

---

## Mapeamento das 6 Etapas do Desafio DIO

O projeto cumpre com excelência todos os requisitos do laboratório da DIO:

| Etapa | Descrição | Arquivo no Repositório |
|:-----:|-----------|------------------------|
| **1** | **Documentação do Agente** | [`docs/01-documentacao-agente.md`](./docs/01-documentacao-agente.md) — Caso de uso, persona financeira, tom de voz, arquitetura e segurança. |
| **2** | **Base de Conhecimento** | [`docs/02-base-conhecimento.md`](./docs/02-base-conhecimento.md) — Estrutura dos dados mockados em [`data/`](./data/) e integração via Pandas/JSON. |
| **3** | **Prompts do Agente** | [`docs/03-prompts.md`](./docs/03-prompts.md) — System prompt estruturado, hiperparâmetros de inferência, few-shots e tratamento de edge cases. |
| **4** | **Aplicação Funcional** | [`src/app.py`](./src/app.py) & [`src/agente.py`](./src/agente.py) — Assistente de terminal interativo com análise de dados e conexões REST. |
| **5** | **Avaliação e Métricas** | [`docs/04-metricas.md`](./docs/04-metricas.md) — Testes automatizados com 100% de sucesso e métricas de qualidade de resposta. |
| **6** | **Pitch (3 Minutos)** | [`docs/05-pitch.md`](./docs/05-pitch.md) — Roteiro executivo de apresentação cronometrado em 3 minutos para bancas e lideranças. |

---

## Estrutura do Repositório

```text
dio-lab-bia-do-futuro/
│
├── README.md                           # Documentação principal do projeto
├── .gitignore                          # Configuração de arquivos ignorados no Git
│
├── data/                               # Base de conhecimento mockada
│   ├── historico_atendimento.csv       # Histórico de atendimentos anteriores
│   ├── perfil_investidor.json          # Perfil de risco, patrimônio e metas do cliente
│   ├── produtos_financeiros.json       # Catálogo de investimentos homologados
│   └── transacoes.csv                  # Histórico contábil de receitas e despesas
│
├── docs/                               # Entregáveis das etapas de documentação
│   ├── 01-documentacao-agente.md       # Persona, caso de uso e arquitetura
│   ├── 02-base-conhecimento.md         # Estratégia de integração com Pandas/JSON
│   ├── 03-prompts.md                   # System Prompt, Few-Shot e Edge Cases
│   ├── 04-metricas.md                  # Resultados de testes e métricas de desempenho
│   └── 05-pitch.md                     # Roteiro de pitch de alto impacto
│
├── src/                                # Código-fonte da aplicação funcional
│   ├── app.py                          # Aplicação interativa de linha de comando (CLI)
│   ├── agente.py                       # Orquestrador do agente, Pandas e chamadas de API
│   ├── config.py                       # Configurações de caminhos, parâmetros e endpoints
│   ├── requirements.txt                # Dependências essenciais (pandas, requests)
│   ├── test_agente.py                  # Suíte de testes automatizados
│   └── README.md                       # Guia de execução detalhado da aplicação
│
└── assets/                             # Recursos complementares do curso
    ├── README.md
    └── RoteiroLab.md
```

---

## Como Executar a Aplicação

### 1. Clonar o Repositório
```bash
git clone https://github.com/JVZerinho/dio-lab-bia-do-futuro.git
cd dio-lab-bia-do-futuro
```

### 2. Instalar as Dependências
```bash
pip install -r src/requirements.txt
```

### 3. Iniciar o Aurélios
```bash
python src/app.py
```

### 4. Executar os Testes Automatizados
```bash
python src/test_agente.py
```

---

## Menu Principal e Exemplos de Interação

Ao iniciar `python src/app.py`, o assistente apresenta uma interface limpa e intuitiva:

```text
========================================================================
      AURÉLIOS - ASSISTENTE DE INVESTIMENTO E ECONOMIA
   Inteligência Financeira com Base em Dados Concretos (Pandas e JSON)
========================================================================

MENU PRINCIPAL:
[1] Dicas Práticas de Economia e Redução de Gastos
[2] Dicas de Investimento e Alocação Estratégica
[3] Demonstrativo Detalhado de Gastos (Pandas)
[4] Diagnóstico da Reserva de Emergência e Metas
[5] Catálogo de Produtos Homologados
[6] Configurar Provedor de IA (Autônomo / Ollama / Nuvem)
[7] Recarregar Dados da Pasta data/
[0] Encerrar Aplicação
------------------------------------------------------------------------
Digite o número da opção OU escreva sua pergunta diretamente:
------------------------------------------------------------------------
Você: 
```

### Exemplos Práticos de Perguntas Suportadas

O usuário pode digitar **qualquer número de opção** ou **escrever sua dúvida diretamente no prompt**:

1. **Dicas Práticas de Economia:**
   > **Entrada:** `[1]` ou *"Como posso economizar nas compras de supermercado?"*  
   > **Aurélios:** Apresenta técnicas de planejamento semanal com lista, alerta sobre o impacto de pedidos recorrentes em delivery e orienta a distribuição orçamentária pela regra 50/30/20.

2. **Dicas Estratégicas de Investimento:**
   > **Entrada:** `[2]` ou *"Onde devo investir R$ 1.000,00 por mês?"*  
   > **Aurélios:** Recomenda direcionar para o Tesouro Selic ou CDB de liquidez diária até concluir a meta de R$ 15.000,00 da Reserva de Emergência, explicando o poder dos juros compostos a médio prazo.

3. **Demonstrativo Detalhado com Pandas:**
   > **Entrada:** `[3]` ou *"Quanto gastei com moradia no mês?"*  
   > **Aurélios:** Gera a tabela agregada de despesas por categoria com percentuais de participação e saldo livre mensal.

4. **Conceitos de Mercado Financeiro:**
   > **Entrada:** *"O que é Taxa Selic?"*, *"Como funciona o FGC?"*, *"Vale mais a pena CDB ou LCI?"*  
   > **Aurélios:** Responde didaticamente, comparando liquidez, segurança, incidência de impostos e prazos de resgate.

5. **Tratamento de Segurança e Escopo:**
   > **Entrada:** *"Qual a minha senha bancária?"* ou *"Quem ganhou o jogo de ontem?"*  
   > **Aurélios:** Recusa educadamente perguntas fora do escopo financeiro e bloqueia rigorosamente solicitações de dados sigilosos conforme diretrizes de segurança da informação e LGPD.

---

## Tecnologias e Bibliotecas

| Tecnologia | Função no Projeto |
|------------|-------------------|
| **Python 3.10+** | Linguagem principal do ecossistema |
| **Pandas** | Agregações estatísticas, cálculos de saldo e categorização contábil |
| **JSON** | Armazenamento estruturado de perfis e catálogos homologados |
| **Requests** | Comunicação HTTP REST com endpoints de LLM (Ollama, OpenAI, Groq) |
| **Terminal CLI** | Interface limpa, responsiva, sem dependências web quebradas |
| **Mermaid** | Diagramação da arquitetura e fluxos de dados do agente |

---

## Autor e Agradecimentos

Projeto desenvolvido por **João Victor** como entrega prática para o bootcamp da **Digital Innovation One (DIO)** em parceria com as lideranças educacionais de inteligência artificial.

*“A felicidade da sua vida depende da qualidade dos seus pensamentos — e da disciplina com suas finanças.”* — Marco Aurélio.
